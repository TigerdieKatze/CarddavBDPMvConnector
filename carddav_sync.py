import os
import json
import logging
import requests
import vdirsyncer.storage
import vdirsyncer.exceptions
import vobject
from typing import List, Tuple, Dict
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pandas as pd

# Load configuration from environment variables
def load_config():
    return {
        "CARDDAV_URL": os.environ["CARDDAV_URL"],
        "USERNAME": os.environ["USERNAME"],
        "PASSWORD": os.environ["PASSWORD"],
        "GROUP_MAPPING": json.loads(os.environ.get("GROUP_MAPPING", '{}')),
        "DEFAULT_GROUP": os.environ.get("DEFAULT_GROUP", "gesammter Stamm"),
        "APPLY_GROUP_MAPPING_TO_PARENTS": os.environ.get("APPLY_GROUP_MAPPING_TO_PARENTS", "False").lower() == "true",
        "APPLY_DEFAULT_GROUP_TO_PARENTS": os.environ.get("APPLY_DEFAULT_GROUP_TO_PARENTS", "True").lower() == "true",
        "RUN_SCHEDULE": os.environ.get("RUN_SCHEDULE", "single"),
        "NOTIFICATION_EMAIL": os.environ["NOTIFICATION_EMAIL"],
        "SMTP_SERVER": os.environ["SMTP_SERVER"],
        "SMTP_PORT": int(os.environ["SMTP_PORT"]),
        "SMTP_USERNAME": os.environ["SMTP_USERNAME"],
        "SMTP_PASSWORD": os.environ["SMTP_PASSWORD"],
        "STATE_FILE": os.environ.get("STATE_FILE", "/app/dangling_contacts_state.json"),
        "MV_USERNAME": os.environ["MV_USERNAME"],
        "MV_PASSWORD": os.environ["MV_PASSWORD"],
        "LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO"),
        "DRY_RUN": os.environ.get("DRY_RUN", "False").lower() == "true",  # New configuration option
    }

CONFIG = load_config()

# Configure logging
logging.basicConfig(level=getattr(logging, CONFIG["LOG_LEVEL"]), 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserDto:
    def __init__(self, firstname: str, lastname: str, own_email: str, secondary_email: str, parent_email: str, groups: List[str]):
        self.firstname = firstname
        self.lastname = lastname
        self.own_email = own_email
        secondary_email = secondary_email
        self.parent_email = parent_email
        self.groups = groups

    @property
    def fullname(self) -> str:
        return f"{self.firstname} {self.lastname}"
    
    

def fetch_contacts() -> List[Tuple[str, str, str]]:
    storage = vdirsyncer.storage.CardDAVStorage(
        url=CONFIG["CARDDAV_URL"],
        username=CONFIG["USERNAME"],
        password=CONFIG["PASSWORD"]
    )

    try:
        storage.discover()
        return list(storage.list())
    except vdirsyncer.exceptions.UserError as e:
        logger.error(f"Error fetching contacts: {e}")
        return []

def update_or_create_contact_card(storage: vdirsyncer.storage.CardDAVStorage, contacts: List[Tuple[str, str, str]], user: UserDto):
    user_vcard, user_href, user_etag = find_or_create_vcard(contacts, user.fullname)
    update_vcard(user_vcard, user, is_parent=False)

    if user.parent_email:
        parent_vcard, parent_href, parent_etag = find_or_create_vcard(contacts, f"{user.fullname} (Eltern)")
        update_vcard(parent_vcard, user, is_parent=True)
        save_vcard(storage, parent_vcard, parent_href, parent_etag)

    save_vcard(storage, user_vcard, user_href, user_etag)

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

def save_vcard(storage: vdirsyncer.storage.CardDAVStorage, vcard: vobject.vCard, href: str, etag: str):
    if CONFIG["DRY_RUN"]:
        action = "Would update" if href else "Would create"
        logger.info(f"[DRY RUN] {action} contact card for: {vcard.fn.value}")
    else:
        if href and etag:
            storage.update(href, vcard.serialize(), etag)
        else:
            storage.upload(vcard.serialize())
        logger.info(f"{'Updated' if href else 'Created'} contact card for: {vcard.fn.value}")

def convert_excel_to_userdto(file_path: str) -> List[UserDto]:
    df = pd.read_excel(file_path)

    users = []
    for _, row in df.iterrows():
        status = row['Status']
        if status.lower() != "aktiv":
            continue
        firstname = row['Vorname']
        lastname = row['Nachname']
        own_email = row['eMail']
        secondary_email = row['eMail2']
        parent_email = row['eMail_Eltern']

        if pd.notna(own_email) and pd.notna(secondary_email) and pd.notna(parent_email):
            continue
        
        groups = []
        if pd.notna(row['Kleingruppe']):
            groups.append(row['Kleingruppe'])

        user = UserDto(
            firstname=firstname,
            lastname=lastname,
            own_email=own_email,
            secondary_email=secondary_email,
            parent_email=parent_email,
            groups=groups
        )
        users.append(user)

    return users

def fetch_users_from_mv() -> List[UserDto]:
    auth_url = "https://mv.meinbdp.de/ica/rest/nami/auth/manual/sessionStartup"
    auth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8"
    }
    auth_data = {
        "username": CONFIG["MV_USERNAME"],
        "password": CONFIG["MV_PASSWORD"],
        "redirectTo": "app.jsp",
        "Login": "Anmelden"
    }

    session = requests.Session()

    auth_response = session.post(auth_url, headers=auth_headers, data=auth_data)

    if auth_response.status_code == 200:
        logger.info("Authentication successful!")
    else:
        logger.error(f"Authentication failed with status code: {auth_response.status_code}")
        logger.error(auth_response.text)
        return []

    get_url = "https://mv.meinbdp.de/ica/rest/nami/search-multi/export-result-list"
    params = {
        'searchedValues': '{"vorname":"","nachname":"","spitzname":"","mitgliedsNummber":"","mglWohnort":"","alterVon":"","alterBis":"","mglStatusId":null,"funktion":"","mglTypeId":[],"organisation":"","tagId":[],"bausteinIncludedId":[],"zeitschriftenversand":false,"searchName":"","taetigkeitId":[],"untergliederungId":[],"mitAllenTaetigkeiten":false,"withEndedTaetigkeiten":false,"ebeneId":null,"grpNummer":"","grpName":"","gruppierung1Id":null,"gruppierung2Id":null,"gruppierung3Id":null,"gruppierung4Id":null,"gruppierung5Id":null,"gruppierung6Id":null,"inGrp":false,"unterhalbGrp":false,"privacy":"","searchType":"MITGLIEDER"}',
        'reportType': 7
    }

    get_response = session.get(get_url, params=params)

    if get_response.status_code == 200:
        logger.info("Data fetched successfully!")
    
        output_file = "/tmp/fetched_data.xlsx"
    
        with open(output_file, "wb") as file:
            file.write(get_response.content)
    
        logger.info(f"Data saved to {output_file}")

        users = convert_excel_to_userdto(output_file)

        try:
            os.remove(output_file)
            logger.info(f"Temporary file {output_file} has been deleted.")
        except OSError as e:
            logger.error(f"Error deleting temporary file {output_file}: {e}")

        return users
    else:
        logger.error(f"GET request failed with status code: {get_response.status_code}")
        logger.error(get_response.text)
        return []

def load_dangling_contacts_state() -> Dict[str, Dict]:
    if os.path.exists(CONFIG["STATE_FILE"]):
        with open(CONFIG["STATE_FILE"], "r") as f:
            return json.load(f)
    return {}

def save_dangling_contacts_state(state: Dict[str, Dict]):
    with open(CONFIG["STATE_FILE"], "w") as f:
        json.dump(state, f)

def send_email(subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = CONFIG["SMTP_USERNAME"]
    msg['To'] = CONFIG["NOTIFICATION_EMAIL"]
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(CONFIG["SMTP_SERVER"], CONFIG["SMTP_PORT"]) as server:
            server.starttls()
            server.login(CONFIG["SMTP_USERNAME"], CONFIG["SMTP_PASSWORD"])
            server.send_message(msg)
        logger.info(f"Email sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def check_dangling_contacts(storage: vdirsyncer.storage.CardDAVStorage, contacts: List[Tuple[str, str, str]], mv_users: List[UserDto]):
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
                        storage.delete(href, etag)
                        del dangling_state[vcard.fn.value]
                        send_email(
                            "Dangling Contact Deleted",
                            f"Dangling contact has been automatically deleted: {vcard.fn.value}\nFirst seen on: {dangling_state[vcard.fn.value]['first_seen']}"
                        )
            else:
                if vcard.fn.value in dangling_state:
                    del dangling_state[vcard.fn.value]

    save_dangling_contacts_state(dangling_state)

def sync_contacts():
    storage = vdirsyncer.storage.CardDAVStorage(
        url=CONFIG["CARDDAV_URL"],
        username=CONFIG["USERNAME"],
        password=CONFIG["PASSWORD"]
    )
    
    contacts = fetch_contacts()
    mv_users = fetch_users_from_mv()
    
    for user in mv_users:
        update_or_create_contact_card(storage, contacts, user)
    
    check_dangling_contacts(storage, contacts, mv_users)

def main():
    if CONFIG["RUN_SCHEDULE"] == "daily":
        schedule.every().day.at("04:00").do(sync_contacts)
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        sync_contacts()

if __name__ == "__main__":
    main()