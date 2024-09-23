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

def connect_to_carddav():
    return requests.Session()

def fetch_contacts(session: requests.Session) -> List[Tuple[str, str, str]]:
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
    
    response = session.request('REPORT', url, headers=headers, data=body, auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
    response.raise_for_status()

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

    return contacts

def update_or_create_contact_card(session, contacts: List[Tuple[str, str, str]], user: UserDto):
    user_vcard, user_href, user_etag = find_or_create_vcard(contacts, user.fullname)
    update_vcard(user_vcard, user, is_parent=False)

    if user.parent_email:
        parent_vcard, parent_href, parent_etag = find_or_create_vcard(contacts, f"{user.fullname} (Eltern)")
        update_vcard(parent_vcard, user, is_parent=True)
        save_vcard(session, parent_vcard, parent_href, parent_etag)

    save_vcard(session, user_vcard, user_href, user_etag)

def find_or_create_vcard(contacts: List[Tuple[str, str, str]], fullname: str) -> Tuple[vobject.vCard, str, str]:
    for href, etag, vcard_string in contacts:
        vcard = vobject.readOne(vcard_string)
        if vcard.fn.value == fullname:
            return vcard, href, etag
    return vobject.vCard(), None, None

def update_vcard(vcard: vobject.vCard, user: UserDto, is_parent: bool):
    vcard.add('fn').value = f"{user.fullname}{' (Eltern)' if is_parent else ''}"
    vcard.add('n').value = vobject.vcard.Name(family=user.lastname, given=user.firstname)
    vcard.add('email').value = user.parent_email if is_parent else user.own_email
    update_group_membership(vcard, user.groups, is_parent)
    add_connector_info(vcard)

def update_group_membership(vcard: vobject.vCard, groups: List[str], is_parent: bool):
    mapped_groups = apply_group_mapping(groups, is_parent)
    final_groups = add_default_group(mapped_groups, is_parent)
    categories = vcard.add('categories')
    categories.value = final_groups + (['Eltern'] if is_parent else [])

def apply_group_mapping(groups: List[str], is_parent: bool) -> List[str]:
    mapped_groups = groups.copy()
    
    if not is_parent or CONFIG["APPLY_GROUP_MAPPING_TO_PARENTS"]:
        for group in groups:
            if group in CONFIG["GROUP_MAPPING"]:
                mapped_group = CONFIG["GROUP_MAPPING"][group]
                if mapped_group not in mapped_groups:
                    mapped_groups.append(mapped_group)

    return mapped_groups

def add_default_group(groups: List[str], is_parent: bool) -> List[str]:
    if not is_parent or CONFIG["APPLY_DEFAULT_GROUP_TO_PARENTS"]:
        if CONFIG["DEFAULT_GROUP"] not in groups:
            groups.append(CONFIG["DEFAULT_GROUP"])
    return groups

def add_connector_info(vcard: vobject.vCard):
    NOTE_TEXT = "Updated automatically via Python MV Connector"
    if 'note' not in vcard.contents or vcard.note.value != NOTE_TEXT:
        vcard.add('note').value = NOTE_TEXT

def save_vcard(session, vcard: vobject.vCard, href: str, etag: str):
    if CONFIG["DRY_RUN"]:
        action = "Would update" if href else "Would create"
        logger.info(f"[DRY RUN] {action} contact card for: {vcard.fn.value}")
    else:
        url = f"{CONFIG['CARDDAV_URL']}{href}" if href else f"{CONFIG['CARDDAV_URL']}{vcard.uid.value}.vcf"
        headers = {
            'Content-Type': 'text/vcard; charset=utf-8',
            'If-Match': etag
        } if etag else {'Content-Type': 'text/vcard; charset=utf-8'}

        vcard_data = vcard.serialize()
        
        if href:
            # Update existing vCard
            response = session.put(url, data=vcard_data, headers=headers, auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
        else:
            # Create new vCard
            response = session.put(url, data=vcard_data, headers=headers, auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
        
        response.raise_for_status()
        new_etag = response.headers.get('ETag', '').strip('"')
        
        action = "Updated" if href else "Created"
        logger.info(f"{action} contact card for: {vcard.fn.value}")
        return (response.url, new_etag)

def load_dangling_contacts_state() -> Dict[str, Dict]:
    if os.path.exists(CONFIG["STATE_FILE"]):
        with open(CONFIG["STATE_FILE"], "r") as f:
            return json.load(f)
    return {}

def save_dangling_contacts_state(state: Dict[str, Dict]):
    with open(CONFIG["STATE_FILE"], "w") as f:
        json.dump(state, f)

def check_dangling_contacts(session, contacts: List[Tuple[str, str, str]], mv_users: List[UserDto]):
    mv_user_names = set([user.fullname for user in mv_users] + [f"{user.fullname} (Eltern)" for user in mv_users if user.parent_email])
    dangling_state = load_dangling_contacts_state()
    current_date = datetime.now().strftime("%Y-%m-%d")

    for href, etag, vcard_string in contacts:
        vcard = vobject.readOne(vcard_string)
        if 'note' in vcard.contents and vcard.note.value == "Updated automatically via Python MV Connector":
            if vcard.fn.value not in mv_user_names:
                if vcard.fn.value not in dangling_state:
                    dangling_state[vcard.fn.value] = {"first_seen": current_date, "count": 1}
                    send_email(
                        "Dangling Contact Found",
                        f"Dangling contact found: {vcard.fn.value}\nFirst seen on: {current_date}\nThis contact will be automatically deleted after 7 consecutive days."
                    )
                else:
                    dangling_state[vcard.fn.value]["count"] += 1
                    if dangling_state[vcard.fn.value]["count"] == 4:
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
        
        response = session.delete(url, headers=headers, auth=HTTPBasicAuth(CONFIG['CARDDAV_USERNAME'], CONFIG['CARDDAV_PASSWORD']))
        response.raise_for_status()
        
        logger.info(f"Deleted contact card: {href}")

def sync_contacts():
    session = connect_to_carddav()
    contacts = fetch_contacts(session)
    mv_users = fetch_users_from_mv()
    
    for user in mv_users:
        update_or_create_contact_card(session, contacts, user)
    
    check_dangling_contacts(session, contacts, mv_users)