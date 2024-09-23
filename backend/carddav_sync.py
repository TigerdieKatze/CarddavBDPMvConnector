import pandas as pd
import requests
import vobject
from typing import List, Tuple, Dict
from datetime import datetime
import os
import json
from config import CONFIG, logger
from mv_integration import fetch_users_from_mv
from notifications import send_email
from models import UserDto
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import time
import uuid
from urllib.parse import urlparse

def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

def connect_to_carddav():
    logger.info("Connecting to CardDAV server")
    return requests.Session()

@log_execution_time
def fetch_contacts(session: requests.Session) -> List[Tuple[str, str, str]]:
    logger.info("Fetching contacts from CardDAV server")
    url = CONFIG['CARDDAV_URL']
    headers = {
        'Depth': '1',
        'Content-Type': 'application/xml; charset=utf-8'
    }
    body = """
    <c:addressbook-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:carddav">
        <d:prop>
            <d:getetag />
            <c:address-data />
        </d:prop>
    </c:addressbook-query>
    """
    
    try:
        response = session.request('REPORT', url, headers=headers, data=body, auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching contacts from CardDAV server: {str(e)}")
        raise

    contacts = []
    root = ET.fromstring(response.content)
    ns = {
        'd': 'DAV:',
        'c': 'urn:ietf:params:xml:ns:carddav'
    }
    for response_elem in root.findall('.//d:response', ns):
        href = response_elem.find('d:href', ns).text
        etag = response_elem.find('.//d:getetag', ns).text.strip('"')
        vcard_data = response_elem.find('.//c:address-data', ns).text
        contacts.append((href, etag, vcard_data))

    logger.info(f"Fetched {len(contacts)} contacts from CardDAV server")
    return contacts

@log_execution_time
def update_or_create_contact_card(session, contacts: List[Tuple[str, str, str]], user: UserDto):
    logger.info(f"Updating or creating contact card for user: {user.fullname}")
    user_vcard, user_href, user_etag = find_or_create_vcard(contacts, user.fullname)
    update_vcard(user_vcard, user, is_parent=False)

    if pd.notna(user.parent_email):
        logger.info(f"Updating or creating parent contact card for user: {user.fullname}")
        parent_vcard, parent_href, parent_etag = find_or_create_vcard(contacts, f"{user.fullname} (Eltern)")
        update_vcard(parent_vcard, user, is_parent=True)
        save_vcard(session, parent_vcard, parent_href, parent_etag)

    save_vcard(session, user_vcard, user_href, user_etag)

def find_or_create_vcard(contacts: List[Tuple[str, str, str]], fullname: str) -> Tuple[vobject.vCard, str, str]:
    for href, etag, vcard_string in contacts:
        vcard = vobject.readOne(vcard_string)
        if vcard.fn.value == fullname:
            logger.debug(f"Found existing vCard for {fullname}")
            return vcard, href, etag
    logger.debug(f"Creating new vCard for {fullname}")
    return vobject.vCard(), None, None


def generate_uid():
    return f"urn:uuid:{uuid.uuid4()}"

def safe_string(value):
    if isinstance(value, str):
        return value.strip()
    elif pd.isna(value) or value is None:
        return ""
    else:
        return str(value).strip()

def get_user_email(user: UserDto, is_parent: bool) -> str:
    if is_parent:
        if pd.isna(user.parent_email):
            raise ValueError(f"Parent email is required for creating Parent VCard of {user.fullname}")
        return safe_string(user.parent_email)
    
    if user.own_email and safe_string(user.own_email):
        return safe_string(user.own_email)
    elif user.secondary_email and safe_string(user.secondary_email):
        logger.warning(f"Using secondary email for {user.fullname} as primary email is empty")
        return safe_string(user.secondary_email)
    else:
        raise ValueError(f"No valid email found for {user.fullname}")

def update_vcard(vcard: vobject.vCard, user: UserDto, is_parent: bool):
    logger.debug(f"Updating vCard for {'parent of ' if is_parent else ''}{user.fullname}")
    
    if 'uid' not in vcard.contents:
        vcard.add('uid').value = generate_uid()
        logger.debug(f"Generated new UID for {user.fullname}")

    fn_value = f"{safe_string(user.fullname)}{' (Eltern)' if is_parent else ''}"
    if 'fn' in vcard.contents:
        vcard.fn.value = fn_value
    else:
        vcard.add('fn').value = fn_value

    n_value = vobject.vcard.Name(family=safe_string(user.lastname), given=safe_string(user.firstname))
    if 'n' in vcard.contents:
        vcard.n.value = n_value
    else:
        vcard.add('n').value = n_value

    try:
        email_value = get_user_email(user, is_parent)
        if 'email' in vcard.contents:
            vcard.email.value = email_value
        else:
            vcard.add('email').value = email_value
    except ValueError as e:
        logger.error(str(e))
        raise

    update_group_membership(vcard, user.groups, is_parent)
    add_connector_info(vcard)

def update_group_membership(vcard: vobject.vCard, groups: List[str], is_parent: bool):
    logger.debug(f"Updating group membership for {'parent' if is_parent else 'user'}")
    mapped_groups = apply_group_mapping(groups, is_parent)
    final_groups = add_default_group(mapped_groups, is_parent)
    
    # Add 'Eltern' category for parent contacts
    if is_parent:
        final_groups.append('Eltern')
    
    # Update or add CATEGORIES
    if 'categories' in vcard.contents:
        vcard.categories.value = final_groups
    else:
        vcard.add('categories').value = final_groups

def apply_group_mapping(groups: List[str], is_parent: bool) -> List[str]:
    mapped_groups = groups.copy()
    
    if not is_parent or CONFIG["APPLY_GROUP_MAPPING_TO_PARENTS"]:
        for group in groups:
            if group in CONFIG["GROUP_MAPPING"]:
                mapped_group = CONFIG["GROUP_MAPPING"][group]
                if mapped_group not in mapped_groups:
                    mapped_groups.append(mapped_group)
                    logger.info(f"Added mapped group: {mapped_group}")

    return mapped_groups

def add_default_group(groups: List[str], is_parent: bool) -> List[str]:
    if not is_parent or CONFIG["APPLY_DEFAULT_GROUP_TO_PARENTS"]:
        if CONFIG["DEFAULT_GROUP"] not in groups:
            groups.append(CONFIG["DEFAULT_GROUP"])
            logger.info(f"Added default group: {CONFIG['DEFAULT_GROUP']}")
    return groups

def add_connector_info(vcard: vobject.vCard):
    NOTE_TEXT = "Updated automatically via Python MV Connector"
    if 'note' not in vcard.contents or vcard.note.value != NOTE_TEXT:
        vcard.add('note').value = NOTE_TEXT

@log_execution_time
def save_vcard(session, vcard: vobject.vCard, href: str, etag: str):
    if CONFIG["DRY_RUN"]:
        action = "Would update" if href else "Would create"
        logger.info(f"[DRY RUN] {action} contact card for: {vcard.fn.value}")
    else:
        parsed_uri = urlparse(CONFIG['CARDDAV_URL'])
        url = f"{parsed_uri.scheme}://{parsed_uri.netloc}{href}" if href else f"{CONFIG['CARDDAV_URL']}/{vcard.uid.value}.vcf"
        headers = {
            'Content-Type': 'text/vcard; charset=utf-8',
            'If-Match': etag
        } if etag else {'Content-Type': 'text/vcard; charset=utf-8'}
        logger.info(f"Saving vcard with url: {url}")

        vcard_data = vcard.serialize()
        
        try:
            response = session.put(url, data=vcard_data, headers=headers, auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
            
            response.raise_for_status()
            new_etag = response.headers.get('ETag', '').strip('"')
            
            action = "Updated" if href else "Created"
            logger.info(f"{action} contact card for: {vcard.fn.value}")
            return (response.url, new_etag)
        except requests.RequestException as e:
            logger.error(f"Error saving vCard for {vcard.fn.value}: {str(e)}")
            raise

def load_dangling_contacts_state() -> Dict[str, Dict]:
    state_file = CONFIG["STATE_FILE"]
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {state_file}. Starting with empty state.")
            return {}
    return {}

def save_dangling_contacts_state(state: Dict[str, Dict]):
    state_file = CONFIG["STATE_FILE"]
    try:
        with open(state_file, "w") as f:
            json.dump(state, f)
    except IOError as e:
        logger.error(f"Error saving dangling contacts state: {str(e)}")

@log_execution_time
def check_dangling_contacts(session, contacts: List[Tuple[str, str, str]], mv_users: List[UserDto]):
    logger.info("Checking for dangling contacts")
    mv_user_names = set([user.fullname for user in mv_users] + [f"{user.fullname} (Eltern)" for user in mv_users if user.parent_email])
    dangling_state = load_dangling_contacts_state()
    current_date = datetime.now().strftime("%Y-%m-%d")

    for href, etag, vcard_string in contacts:
        vcard = vobject.readOne(vcard_string)
        if 'note' in vcard.contents and vcard.note.value == "Updated automatically via Python MV Connector":
            if vcard.fn.value not in mv_user_names:
                if vcard.fn.value not in dangling_state:
                    dangling_state[vcard.fn.value] = {"first_seen": current_date, "count": 1}
                    logger.warning(f"New dangling contact found: {vcard.fn.value}")
                    send_email(
                        "Dangling Contact Found",
                        f"Dangling contact found: {vcard.fn.value}\nFirst seen on: {current_date}\nThis contact will be automatically deleted after 7 consecutive days."
                    )
                else:
                    dangling_state[vcard.fn.value]["count"] += 1
                    if dangling_state[vcard.fn.value]["count"] == 4:
                        logger.warning(f"Dangling contact reminder: {vcard.fn.value}")
                        send_email(
                            "Dangling Contact Reminder",
                            f"Dangling contact reminder: {vcard.fn.value}\nFirst seen on: {dangling_state[vcard.fn.value]['first_seen']}\nThis contact will be automatically deleted in 3 days if it remains dangling."
                        )
                    elif dangling_state[vcard.fn.value]["count"] >= 7:
                        logger.warning(f"Deleting dangling contact: {vcard.fn.value}")
                        delete_vcard(session, href, etag)
                        del dangling_state[vcard.fn.value]
                        send_email(
                            "Dangling Contact Deleted",
                            f"Dangling contact has been automatically deleted: {vcard.fn.value}\nFirst seen on: {dangling_state[vcard.fn.value]['first_seen']}"
                        )
            else:
                if vcard.fn.value in dangling_state:
                    del dangling_state[vcard.fn.value]

    save_dangling_contacts_state(dangling_state)

def delete_vcard(session, href: str, etag: str):
    if CONFIG["DRY_RUN"]:
        logger.info(f"[DRY RUN] Would delete contact card: {href}")
    else:
        url = f"{CONFIG['CARDDAV_URL']}{href}"
        headers = {'If-Match': etag} if etag else {}
        
        try:
            response = session.delete(url, headers=headers, auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
            response.raise_for_status()
            logger.info(f"Deleted contact card: {href}")
        except requests.RequestException as e:
            logger.error(f"Error deleting vCard {href}: {str(e)}")
            raise

@log_execution_time
def sync_contacts():
    logger.info("Starting contact synchronization")
    failed_contacts = []
    try:
        session = connect_to_carddav()
        contacts = fetch_contacts(session)
        mv_users = fetch_users_from_mv()
        
        for user in mv_users:
            try:
                update_or_create_contact_card(session, contacts, user)
            except Exception as e:
                logger.error(f"Error processing user {user.fullname}: {str(e)}")
                failed_contacts.append((user.fullname, str(e)))
        
        check_dangling_contacts(session, contacts, mv_users)
        logger.info("Contact synchronization completed")
    except Exception as e:
        logger.error(f"Error during contact synchronization: {str(e)}")
        send_email(
            "Synchronization Error",
            f"An error occurred during contact synchronization: {str(e)}"
        )
    finally:
        if failed_contacts:
            logger.error("The following contacts failed to sync:")
            for name, error in failed_contacts:
                logger.error(f"- {name}: {error}")
            send_email(
                "Failed Contacts During Sync",
                "The following contacts failed to sync:\n" + 
                "\n".join([f"- {name}: {error}" for name, error in failed_contacts])
            )
        else:
            logger.info("All contacts synced successfully")