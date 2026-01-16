"""
risk_engine.py

PURPOSE:
- Merge cleaned Aadhaar datasets (biometric, demographic, enrolment)
- Compute behavioural risk indicators
- Generate district-level and state-level risk percentages (0–100)

THIS IS THE CORE INTELLIGENCE LAYER OF ARIS
"""

import os
import pandas as pd
import numpy as np

# --------------------------------------------------
# Paths
# --------------------------------------------------
CLEAN_DIR = "data/cleaned"
OUT_DIR = "data/processed"

os.makedirs(OUT_DIR, exist_ok=True)

# --------------------------------------------------
# Load cleaned datasets
# --------------------------------------------------
def load_data():
    """
    Load cleaned CSVs generated from API pipeline
    """

    bio = pd.read_csv(os.path.join(CLEAN_DIR, "biometric_cleaned.csv"))
    demo = pd.read_csv(os.path.join(CLEAN_DIR, "demographic_cleaned.csv"))
    enrol = pd.read_csv(os.path.join(CLEAN_DIR, "enrolment_cleaned.csv"))

    return bio, demo, enrol

# --------------------------------------------------
# Feature engineering
# --------------------------------------------------
def build_features():
    """
    Merge datasets and compute risk signals
    """

    bio, demo, enrol = load_data()

    # --------------------------------------------------
    # Aggregate monthly data at district level
    # --------------------------------------------------
    bio_agg = (
        bio
        .groupby(["state", "district", "year", "month"], as_index=False)
        .agg(
            bio_5_17=("bio_5_17", "sum"),
            bio_17_plus=("bio_17_plus", "sum")
        )
    )

    demo_agg = (
        demo
        .groupby(["state", "district", "year", "month"], as_index=False)
        .agg(
            demo_5_17=("demo_5_17", "sum"),
            demo_17_plus=("demo_17_plus", "sum")
        )
    )

    enrol_agg = (
        enrol
        .groupby(["state", "district", "year", "month"], as_index=False)
        .agg(
            enrolment_count=("enrolment_count", "sum")
        )
    )

    # --------------------------------------------------
    # Merge all datasets
    # --------------------------------------------------
    df = (
        bio_agg
        .merge(demo_agg, on=["state", "district", "year", "month"], how="left")
        .merge(enrol_agg, on=["state", "district", "year", "month"], how="left")
    )

    # Fill missing values safely
    df = df.fillna(0)

    # --------------------------------------------------
    # Core behavioural indicators
    # --------------------------------------------------

    # Total updates
    df["total_bio_updates"] = df["bio_5_17"] + df["bio_17_plus"]
    df["total_demo_updates"] = df["demo_5_17"] + df["demo_17_plus"]

    # Update intensity (per enrolment)
    df["bio_update_rate"] = df["total_bio_updates"] / (df["enrolment_count"] + 1)
    df["demo_update_rate"] = df["total_demo_updates"] / (df["enrolment_count"] + 1)

    # Age skew (child vs adult)
    df["bio_age_skew"] = df["bio_5_17"] / (df["bio_17_plus"] + 1)
    df["demo_age_skew"] = df["demo_5_17"] / (df["demo_17_plus"] + 1)

    # --------------------------------------------------
    # Month-over-month volatility
    # --------------------------------------------------
    df = df.sort_values(["state", "district", "year", "month"])

    df["bio_mom_change"] = (
        df.groupby(["state", "district"])["bio_update_rate"]
        .pct_change()
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
        .abs()
    )

    df["demo_mom_change"] = (
        df.groupby(["state", "district"])["demo_update_rate"]
        .pct_change()
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
        .abs()
    )

    # --------------------------------------------------
    # Composite risk signal (explainable weights)
    # --------------------------------------------------
    df["risk_signal"] = (
        0.30 * df["bio_update_rate"] +
        0.25 * df["demo_update_rate"] +
        0.20 * df["bio_age_skew"] +
        0.15 * df["demo_age_skew"] +
        0.10 * (df["bio_mom_change"] + df["demo_mom_change"])
    )

    # --------------------------------------------------
    # Convert signal to risk percentage (0–100)
    # --------------------------------------------------
    df["risk_percent"] = (
        df["risk_signal"].rank(pct=True) * 100
    ).round(2)

    return df

# --------------------------------------------------
# Save outputs for frontend
# --------------------------------------------------
def save_outputs(df):
    """
    Save district-level and state-level risk tables
    """

    # District-level risk
    district_risk = (
        df.groupby(["state", "district"], as_index=False)
        .agg(risk_percent=("risk_percent", "mean"))
        .sort_values("risk_percent", ascending=False)
    )

    district_risk.to_csv(
        os.path.join(OUT_DIR, "district_risk.csv"),
        index=False
    )

    # State-level risk
    state_risk = (
        district_risk
        .groupby("state", as_index=False)
        .agg(risk_percent=("risk_percent", "mean"))
        .sort_values("risk_percent", ascending=False)
    )

    state_risk.to_csv(
        os.path.join(OUT_DIR, "state_risk.csv"),
        index=False
    )

    print("✅ Risk tables saved successfully")

# --------------------------------------------------
# Main execution
# --------------------------------------------------
def main():
    print("⚙️ Building risk intelligence...")
    df = build_features()
    save_outputs(df)
    print("🎉 Risk engine completed")

if __name__ == "__main__":
    main()
