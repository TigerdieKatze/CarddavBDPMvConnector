import pandas as pd
import requests
import vobject
from typing import List, Tuple, Dict
from datetime import datetime
import os
import json
import xml.etree.ElementTree as ET
import time
import uuid
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
from config import CONFIG, logger
from mv_integration import fetch_users_from_mv
from notifications import send_email
from models import UserDto

# Utility Functions

def log_execution_time(func):
    """Decorator to log the execution time of functions."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

def safe_string(value):
    """Convert any value to a safe string, raising ValueError for NaN, 'nan', or empty strings."""
    if pd.isna(value):
        raise ValueError("Cannot convert NaN to a string")
    elif isinstance(value, str):
        cleaned = value.strip().lower()
        if not cleaned or cleaned == "nan":
            raise ValueError("Empty string or 'nan' is not allowed")
        return value.strip()
    else:
        result = str(value).strip()
        if not result or result.lower() == "nan":
            raise ValueError("Conversion resulted in an empty string or 'nan'")
        return result

def generate_uid():
    """Generate a unique identifier for vCards."""
    return f"urn:uuid:{uuid.uuid4()}"

# CardDAV Connection and Fetching

def connect_to_carddav():
    """Establish a connection to the CardDAV server."""
    logger.info("Connecting to CardDAV server")
    return requests.Session()

@log_execution_time
def fetch_contacts(session: requests.Session) -> List[Tuple[str, str, str]]:
    """Fetch all contacts from the CardDAV server."""
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
        response = session.request('REPORT', url, headers=headers, data=body, 
                                   auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching contacts from CardDAV server: {str(e)}")
        raise

    contacts = []
    root = ET.fromstring(response.content)
    ns = {'d': 'DAV:', 'c': 'urn:ietf:params:xml:ns:carddav'}
    for response_elem in root.findall('.//d:response', ns):
        href = response_elem.find('d:href', ns).text
        etag = response_elem.find('.//d:getetag', ns).text.strip('"')
        vcard_data = response_elem.find('.//c:address-data', ns).text
        contacts.append((href, etag, vcard_data))

    logger.info(f"Fetched {len(contacts)} contacts from CardDAV server")
    return contacts

# vCard Operations

def find_or_create_vcard(contacts: List[Tuple[str, str, str]], fullname: str) -> Tuple[vobject.vCard, str, str]:
    """Find an existing vCard or create a new one."""
    for href, etag, vcard_string in contacts:
        vcard = vobject.readOne(vcard_string)
        if vcard.fn.value == fullname:
            logger.debug(f"Found existing vCard for {fullname}")
            return vcard, href, etag
    logger.debug(f"Creating new vCard for {fullname}")
    return vobject.vCard(), None, None

def get_user_email(user: UserDto, is_parent: bool) -> str:
    """Get the appropriate email for a user or parent."""
    if is_parent:
        if pd.isna(user.parent_email) or not user.parent_email.strip():
            raise ValueError(f"Valid parent email is required for creating Parent VCard of {user.fullname}")
        return safe_string(user.parent_email)
    
    if not pd.isna(user.own_email) and user.own_email.strip():
        return safe_string(user.own_email)
    elif not pd.isna(user.secondary_email) and user.secondary_email.strip():
        logger.warning(f"Using secondary email for {user.fullname} as primary email is empty")
        return safe_string(user.secondary_email)
    else:
        raise ValueError(f"No valid email found for {user.fullname}")

def update_vcard(vcard: vobject.vCard, user: UserDto, is_parent: bool):
    """Update or create a vCard with user information."""
    logger.debug(f"Updating vCard for {'parent of ' if is_parent else ''}{user.fullname}")
    
    if 'uid' not in vcard.contents:
        vcard.add('uid').value = generate_uid()
    
    fn_value = f"{safe_string(user.fullname)}{' (Eltern)' if is_parent else ''}"
    if 'fn' not in vcard.contents:
        vcard.add('fn').value = fn_value
    else:
        vcard.fn.value = fn_value
    
    n_value = vobject.vcard.Name(family=safe_string(user.lastname), given=safe_string(user.firstname))
    if 'n' not in vcard.contents:
        vcard.add('n').value = n_value
    else:
        vcard.n.value = n_value

    try:
        email_value = get_user_email(user, is_parent)
        if 'email' not in vcard.contents:
            vcard.add('email').value = email_value
        else:
            vcard.email.value = email_value
    except ValueError as e:
        logger.error(str(e))
        raise

    update_group_membership(vcard, user.groups, is_parent)
    add_connector_info(vcard)

def update_group_membership(vcard: vobject.vCard, groups: List[str], is_parent: bool):
    """Update the group membership of a vCard."""
    mapped_groups = apply_group_mapping(groups, is_parent)
    final_groups = add_default_group(mapped_groups, is_parent)
    
    if is_parent:
        final_groups.append('Eltern')
    
    vcard.add('categories').value = final_groups

def apply_group_mapping(groups: List[str], is_parent: bool) -> List[str]:
    """Apply group mapping based on configuration."""
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
    """Add the default group if configured."""
    if not is_parent or CONFIG["APPLY_DEFAULT_GROUP_TO_PARENTS"]:
        if CONFIG["DEFAULT_GROUP"] not in groups:
            groups.append(CONFIG["DEFAULT_GROUP"])
            logger.info(f"Added default group: {CONFIG['DEFAULT_GROUP']}")
    return groups

def add_connector_info(vcard: vobject.vCard):
    """Add a note to indicate the vCard was updated by this connector."""
    NOTE_TEXT = "Updated automatically via Python MV Connector"
    vcard.add('note').value = NOTE_TEXT

@log_execution_time
def save_vcard(session, vcard: vobject.vCard, href: str, etag: str):
    """Save a vCard to the CardDAV server."""
    if CONFIG["DRY_RUN"]:
        action = "Would update" if href else "Would create"
        logger.info(f"[DRY RUN] {action} contact card for: {vcard.fn.value}")
        return

    parsed_uri = urlparse(CONFIG['CARDDAV_URL'])
    url = f"{parsed_uri.scheme}://{parsed_uri.netloc}{href}" if href else f"{CONFIG['CARDDAV_URL']}/{vcard.uid.value}.vcf"
    headers = {
        'Content-Type': 'text/vcard; charset=utf-8',
        'If-Match': etag
    } if etag else {'Content-Type': 'text/vcard; charset=utf-8'}

    try:
        response = session.put(url, data=vcard.serialize(), headers=headers, 
                               auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
        response.raise_for_status()
        action = "Updated" if href else "Created"
        logger.info(f"{action} contact card for: {vcard.fn.value}")
        return (response.url, response.headers.get('ETag', '').strip('"'))
    except requests.RequestException as e:
        logger.error(f"Error saving vCard for {vcard.fn.value}: {str(e)}")
        raise

# Dangling Contacts Management

def load_dangling_contacts_state() -> Dict[str, Dict]:
    """Load the state of dangling contacts from a file."""
    state_file = CONFIG["STATE_FILE"]
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {state_file}. Starting with empty state.")
    return {}

def save_dangling_contacts_state(state: Dict[str, Dict]):
    """Save the state of dangling contacts to a file."""
    state_file = CONFIG["STATE_FILE"]
    try:
        with open(state_file, "w") as f:
            json.dump(state, f)
    except IOError as e:
        logger.error(f"Error saving dangling contacts state: {str(e)}")

@log_execution_time
def check_dangling_contacts(session, contacts: List[Tuple[str, str, str]], mv_users: List[UserDto]):
    """Check for and manage dangling contacts."""
    logger.info("Checking for dangling contacts")
    mv_user_names = set([user.fullname for user in mv_users] + [f"{user.fullname} (Eltern)" for user in mv_users if user.parent_email])
    dangling_state = load_dangling_contacts_state()
    current_date = datetime.now().strftime("%Y-%m-%d")

    for href, etag, vcard_string in contacts:
        vcard = vobject.readOne(vcard_string)
        if 'note' in vcard.contents and vcard.note.value == "Updated automatically via Python MV Connector":
            if vcard.fn.value not in mv_user_names:
                manage_dangling_contact(session, vcard, href, etag, dangling_state, current_date)
            elif vcard.fn.value in dangling_state:
                del dangling_state[vcard.fn.value]

    save_dangling_contacts_state(dangling_state)

def manage_dangling_contact(session, vcard, href, etag, dangling_state, current_date):
    """Manage a single dangling contact."""
    if vcard.fn.value not in dangling_state:
        dangling_state[vcard.fn.value] = {"first_seen": current_date, "count": 1}
        logger.warning(f"New dangling contact found: {vcard.fn.value}")
        send_email("Dangling Contact Found", f"Dangling contact found: {vcard.fn.value}\nFirst seen on: {current_date}\nThis contact will be automatically deleted after 7 consecutive days.")
    else:
        dangling_state[vcard.fn.value]["count"] += 1
        count = dangling_state[vcard.fn.value]["count"]
        if count == 4:
            logger.warning(f"Dangling contact reminder: {vcard.fn.value}")
            send_email("Dangling Contact Reminder", f"Dangling contact reminder: {vcard.fn.value}\nFirst seen on: {dangling_state[vcard.fn.value]['first_seen']}\nThis contact will be automatically deleted in 3 days if it remains dangling.")
        elif count >= 7:
            logger.warning(f"Deleting dangling contact: {vcard.fn.value}")
            delete_vcard(session, href, etag)
            del dangling_state[vcard.fn.value]
            send_email("Dangling Contact Deleted", f"Dangling contact has been automatically deleted: {vcard.fn.value}\nFirst seen on: {dangling_state[vcard.fn.value]['first_seen']}")

def delete_vcard(session, href: str, etag: str):
    """Delete a vCard from the CardDAV server."""
    if CONFIG["DRY_RUN"]:
        logger.info(f"[DRY RUN] Would delete contact card: {href}")
        return

    url = f"{CONFIG['CARDDAV_URL']}{href}"
    headers = {'If-Match': etag} if etag else {}
    
    try:
        response = session.delete(url, headers=headers, auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
        response.raise_for_status()
        logger.info(f"Deleted contact card: {href}")
    except requests.RequestException as e:
        logger.error(f"Error deleting vCard {href}: {str(e)}")
        raise

# Main Synchronization Function

@log_execution_time
def sync_contacts():
    """Main function to synchronize contacts between MV and CardDAV."""
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
        send_email("Synchronization Error", f"An error occurred during contact synchronization: {str(e)}")
    finally:
        if failed_contacts:
            log_failed_contacts(failed_contacts)
        else:
            logger.info("All contacts synced successfully")

def update_or_create_contact_card(session, contacts: List[Tuple[str, str, str]], user: UserDto):
    """Update or create a contact card for a user and their parent if applicable."""
    logger.info(f"Processing user: {user.fullname}")
    errors = []

    # Process user contact
    try:
        user_vcard, user_href, user_etag = find_or_create_vcard(contacts, user.fullname)
        update_vcard(user_vcard, user, is_parent=False)
        save_vcard(session, user_vcard, user_href, user_etag)
    except Exception as e:
        logger.error(f"Error processing user contact for {user.fullname}: {str(e)}")
        errors.append(f"User contact: {str(e)}")

    # Process parent contact if parent email exists
    if pd.notna(user.parent_email) and user.parent_email.lower() != "nan":
        try:
            parent_vcard, parent_href, parent_etag = find_or_create_vcard(contacts, f"{user.fullname} (Eltern)")
            update_vcard(parent_vcard, user, is_parent=True)
            save_vcard(session, parent_vcard, parent_href, parent_etag)
        except Exception as e:
            logger.error(f"Error processing parent contact for {user.fullname}: {str(e)}")
            errors.append(f"Parent contact: {str(e)}")

    # If any errors occurred, raise an exception with all error messages
    if errors:
        raise Exception("; ".join(errors))

def log_failed_contacts(failed_contacts):
    """Log and send an email about failed contacts."""
    logger.error("The following contacts failed to sync:")
    for name, error in failed_contacts:
        logger.error(f"- {name}: {error}")
    send_email(
        "Failed Contacts During Sync",
        "The following contacts failed to sync:\n" + 
        "\n".join([f"- {name}: {error}" for name, error in failed_contacts])
    )