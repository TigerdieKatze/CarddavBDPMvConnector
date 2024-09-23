# mv_integration.py
import requests
import pandas as pd
import os
from typing import List
from config import CONFIG, logger
from models import UserDto

def fetch_users_from_mv() -> List[UserDto]:
    logger.info("Fetching users from MV system")
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
        logger.info("Data fetched successfully from MV system")
    
        output_file = "/tmp/fetched_data.xlsx"
    
        with open(output_file, "wb") as file:
            file.write(get_response.content)
    
        logger.info(f"Data saved to {output_file}")

        users = convert_excel_to_userdto(output_file)

        try:
            os.remove(output_file)
            logger.info(f"Temporary file {output_file} has been deleted")
        except OSError as e:
            logger.error(f"Error deleting temporary file {output_file}: {e}")

        return users
    else:
        logger.error(f"GET request failed with status code: {get_response.status_code}")
        logger.error(get_response.text)
        return []

def safe_string(value):
    if isinstance(value, str):
        return value.strip()
    elif value is None or pd.isna(value):  # Check for None or NaN values
        return ""
    else:
        return str(value).strip()

def convert_excel_to_userdto(file_path: str) -> List[UserDto]:
    logger.info(f"Converting Excel file to UserDto objects: {file_path}")
    df = pd.read_excel(file_path)

    users = []
    for _, row in df.iterrows():
        status = row['Status']
        if status.lower() != "aktiv":
            continue
        firstname = safe_string(row['Vorname'])
        lastname = safe_string(row['Nachname'])
        own_email = safe_string(row['eMail'])
        secondary_email = safe_string(row['eMail2'])
        parent_email = safe_string(row['eMail_Eltern'])

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

    logger.info(f"Converted {len(users)} users from Excel file")
    return users