"""
api_to_clean.py

PURPOSE:
- Fetch LIVE Aadhaar data from UIDAI (data.gov.in) APIs
- Normalize different dataset schemas
- Clean and standardize columns
- Save cleaned CSV files for downstream risk analysis

THIS FILE HANDLES:
- Biometric Monthly Update Data
- Demographic Monthly Update Data
- Enrolment Monthly Data

IMPORTANT:
- Uses API key from .env
- Handles schema variations safely
"""

import os
import pandas as pd

# Import API client functions
from backend.api_clients.uidai_api import (
    get_biometric_updates,
    get_demographic_updates,
    get_enrolment_data
)

# --------------------------------------------------
# Output directory for cleaned data
# --------------------------------------------------
CLEAN_DIR = "data/cleaned"
os.makedirs(CLEAN_DIR, exist_ok=True)

# --------------------------------------------------
# Common cleaning logic for all datasets
# --------------------------------------------------
def clean_common_columns(df):
    """
    Standard cleaning applied to all UIDAI datasets:
    - Lowercase and strip column names
    - Convert date to year and month
    - Clean state and district names
    """

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Handle date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month

    # Clean text fields
    if "state" in df.columns:
        df["state"] = df["state"].astype(str).str.strip().str.title()

    if "district" in df.columns:
        df["district"] = df["district"].astype(str).str.strip().str.title()

    return df

# --------------------------------------------------
# Biometric data cleaning (FIXED VERSION)
# --------------------------------------------------
def process_biometric_data():
    """
    Fetch and clean Aadhaar Biometric Monthly Update Data
    """

    print("📡 Fetching biometric update data from API...")
    df = get_biometric_updates()

    if df.empty:
        print("⚠️ No biometric data fetched")
        return

    # DEBUG: show actual API columns (useful for audits)
    print("🔍 API biometric columns:", df.columns.tolist())

    # Apply common cleaning
    df = clean_common_columns(df)

    # --------------------------------------------------
    # Handle ALL known API column name variations
    # --------------------------------------------------
    column_mapping = {
        # Child biometric updates
        "bio age 5 17": "bio_5_17",
        "bio_age_5_17": "bio_5_17",
        "biometric_age_5_17": "bio_5_17",
        "age_5_17": "bio_5_17",

        # Adult biometric updates (IMPORTANT FIX)
        "bio age 17": "bio_17_plus",
        "bio_age_17": "bio_17_plus",
        "bio_age_17_": "bio_17_plus",   # ← FIXED (trailing underscore)
        "biometric_age_17": "bio_17_plus",
        "age_17_above": "bio_17_plus",
    }

    # Rename columns only if they exist
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})

    # --------------------------------------------------
    # Safety check: required columns must exist
    # --------------------------------------------------
    required_cols = ["bio_5_17", "bio_17_plus"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        raise ValueError(
            f"❌ Required biometric columns missing: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    # --------------------------------------------------
    # Final column selection
    # --------------------------------------------------
    df = df[
        ["state", "district", "year", "month", "bio_5_17", "bio_17_plus"]
    ]

    out_path = os.path.join(CLEAN_DIR, "biometric_cleaned.csv")
    df.to_csv(out_path, index=False)

    print(f"✅ Biometric data cleaned and saved → {out_path}")

# --------------------------------------------------
# Demographic data cleaning
# --------------------------------------------------
def process_demographic_data():
    """
    Fetch and clean Aadhaar Demographic Monthly Update Data

    NOTE:
    Demographic dataset is age-segmented (5–17, 17+),
    similar to biometric data.
    """

    print("📡 Fetching demographic update data from API...")
    df = get_demographic_updates()

    if df.empty:
        print("⚠️ No demographic data fetched – skipping")
        return

    # DEBUG: inspect API schema
    print("🔍 API demographic columns:", df.columns.tolist())

    # Apply common cleaning
    df = clean_common_columns(df)

    # --------------------------------------------------
    # Handle API column name variations (DEMOGRAPHIC)
    # --------------------------------------------------
    column_mapping = {
        # Child demographic updates
        "demo age 5 17": "demo_5_17",
        "demo_age_5_17": "demo_5_17",
        "demographic_age_5_17": "demo_5_17",

        # Adult demographic updates
        "demo age 17": "demo_17_plus",
        "demo_age_17": "demo_17_plus",
        "demo_age_17_": "demo_17_plus",   # ← IMPORTANT FIX
        "demographic_age_17": "demo_17_plus",
    }

    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})

    # --------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------
    required_cols = ["demo_5_17", "demo_17_plus"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        raise ValueError(
            f"❌ Required demographic columns missing: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    # --------------------------------------------------
    # Final column selection
    # --------------------------------------------------
    df = df[
        ["state", "district", "year", "month", "demo_5_17", "demo_17_plus"]
    ]

    out_path = os.path.join(CLEAN_DIR, "demographic_cleaned.csv")
    df.to_csv(out_path, index=False)

    print(f"✅ Demographic data cleaned and saved → {out_path}")



# --------------------------------------------------
# Enrolment data cleaning
# --------------------------------------------------
def process_enrolment_data():
    """
    Fetch and clean Aadhaar Monthly Enrolment Data

    NOTE:
    Enrolment data is age-wise:
    - Age 0–5
    - Age 5–17
    - Age 18+

    We compute total enrolment as the sum of all age groups.
    """

    print("📡 Fetching enrolment data from API...")
    df = get_enrolment_data()

    if df.empty:
        print("⚠️ No enrolment data fetched – skipping")
        return

    # DEBUG: inspect enrolment API schema
    print("🔍 API enrolment columns:", df.columns.tolist())

    # Apply common cleaning
    df = clean_common_columns(df)

    # --------------------------------------------------
    # Handle API column name variations (ENROLMENT)
    # --------------------------------------------------
    column_mapping = {
        # Child enrolment
        "age 0 5": "enrol_0_5",
        "age_0_5": "enrol_0_5",

        # Minor enrolment
        "age 5 17": "enrol_5_17",
        "age_5_17": "enrol_5_17",

        # Adult enrolment
        "age 18 greater": "enrol_18_plus",
        "age_18_greater": "enrol_18_plus",
        "age_18+": "enrol_18_plus",
    }

    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})

    # --------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------
    required_cols = ["enrol_0_5", "enrol_5_17", "enrol_18_plus"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        raise ValueError(
            f"❌ Required enrolment columns missing: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    # --------------------------------------------------
    # Compute total enrolment
    # --------------------------------------------------
    df["enrolment_count"] = (
        df["enrol_0_5"] +
        df["enrol_5_17"] +
        df["enrol_18_plus"]
    )

    # --------------------------------------------------
    # Final column selection
    # --------------------------------------------------
    df = df[
        [
            "state",
            "district",
            "year",
            "month",
            "enrol_0_5",
            "enrol_5_17",
            "enrol_18_plus",
            "enrolment_count"
        ]
    ]

    out_path = os.path.join(CLEAN_DIR, "enrolment_cleaned.csv")
    df.to_csv(out_path, index=False)

    print(f"✅ Enrolment data cleaned and saved → {out_path}")


# --------------------------------------------------
# Main execution
# --------------------------------------------------
def main():
    """
    Run full API → cleaning pipeline
    """

    process_biometric_data()
    process_demographic_data()
    process_enrolment_data()

    print("🎉 API data ingestion and cleaning completed successfully")

if __name__ == "__main__":
    main()
