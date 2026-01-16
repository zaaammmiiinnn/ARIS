"""
uidai_api.py

PURPOSE:
- Connect to data.gov.in (UIDAI open datasets)
- Fetch Aadhaar enrolment / biometric / demographic data via API
- Use API key securely from .env
- Return data in pandas DataFrame format

WHY THIS FILE EXISTS:
- Keeps API logic separate from data processing
- Makes backend modular and clean
- Allows easy switching between datasets
"""

import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables from .env file
# --------------------------------------------------
# This loads DATA_GOV_API_KEY safely into the program
load_dotenv()

API_KEY = os.getenv("DATA_GOV_API_KEY")
BASE_URL = os.getenv("DATA_GOV_BASE_URL")

if not API_KEY:
    raise ValueError("❌ DATA_GOV_API_KEY not found in .env file")

# --------------------------------------------------
# Helper function: call data.gov.in API
# --------------------------------------------------
def fetch_uidai_data(resource_id, years=(2024, 2025), limit=1000):
    """
    Fetch UIDAI data month-wise + paginated
    """

    all_records = []

    for year in years:
        for month in range(1, 13):
            offset = 0
            print(f"📅 Fetching Year={year}, Month={month}")

            while True:
                params = {
                    "api-key": API_KEY,
                    "format": "json",
                    "limit": limit,
                    "offset": offset,
                    "filters": json.dumps({
                        "year": year,
                        "month": month
                    })
                }

                url = f"{BASE_URL}/{resource_id}"
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                records = data.get("records", [])

                if not records:
                    break

                all_records.extend(records)
                offset += limit

            print(f"✅ {year}-{month}: fetched")

    df = pd.DataFrame(all_records)
    print(f"📊 TOTAL RECORDS FETCHED: {len(df)}")
    return df



# --------------------------------------------------
# Dataset-specific wrappers
# --------------------------------------------------

def get_biometric_updates():
    """
    Fetch Aadhaar Biometric Monthly Update Data
    """

    # TODO: Replace this with the ACTUAL resource_id from data.gov.in
    BIOMETRIC_RESOURCE_ID = "65454dab-1517-40a3-ac1d-47d4dfe6891c"

    return fetch_uidai_data(BIOMETRIC_RESOURCE_ID)


def get_demographic_updates():
    """
    Fetch Aadhaar Demographic Monthly Update Data
    """

    # TODO: Replace this with the ACTUAL resource_id from data.gov.in
    DEMOGRAPHIC_RESOURCE_ID = "19eac040-0b94-49fa-b239-4f2fd8677d53"

    return fetch_uidai_data(DEMOGRAPHIC_RESOURCE_ID)


def get_enrolment_data():
    """
    Fetch Aadhaar Monthly Enrolment Data
    """

    # TODO: Replace this with the ACTUAL resource_id from data.gov.in
    ENROLMENT_RESOURCE_ID = "ecd49b12-3084-4521-8f7e-ca8bf72069ba"

    return fetch_uidai_data(ENROLMENT_RESOURCE_ID)
