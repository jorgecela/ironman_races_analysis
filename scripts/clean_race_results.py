"""
clean_race_results.py

────────────────────────────────────────────────────────────────────────────
🧹 Clean and Standardize IRONMAN Race Result Data
────────────────────────────────────────────────────────────────────────────

🔍 What It Does:
---------------
This script loads combined IRONMAN and IRONMAN WC race data, cleans and standardizes it,
and saves the result in both CSV and Parquet formats. It performs:

- Date formatting and year extraction
- Conversion of ranks and times to numeric/timedelta
- Gender inference from division codes
- Filtering out invalid or incomplete entries
- Merging of race types from race metadata

📥 Input:
--------
- Combined CSV files:
  - `all_races_combined.csv`
  - `all_races_and_wc_combined.csv`
- Metadata file:
  - `all_ironman_races.csv` (used to assign Race Type)

📤 Output:
---------
- Cleaned CSV and Parquet files saved to:
  - `data/results/cleaned/cleaned_races_data.csv`
  - `data/results/cleaned/cleaned_races_data.parquet`
  - (and same for wc version)

────────────────────────────────────────────────────────────────────────────
"""

import pandas as pd
import os

# -------------------------------
# File Paths
# -------------------------------

input_files = {
    "data": "data/results/combined/all_races_combined.csv",
    "data_and_wc": "data/results/combined/all_races_and_wc_combined.csv",
    "wc": "data/results/combined/all_races_wc_combined.csv"
}

races_data = pd.read_csv("data/urls/all_ironman_races.csv")

# -------------------------------
# Columns to Convert
# -------------------------------

numeric_cols = ["Year", "Div Rank", "Gender Rank", "Overall Rank"]
time_cols = [
    "Swim Time", "Transition 1", "Bike Time",
    "Transition 2", "Run Time", "Finish Time"
]

# -------------------------------
# Processing Loop
# -------------------------------

for label, path in input_files.items():
    print(f"\n🧼 Processing: {label}")

    df = pd.read_csv(path, low_memory=False)

    # Drop fully empty columns and unnamed index artifacts
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip()

    # Merge Race Type from metadata
    df = df.merge(
        races_data[["Race Name", "Race Type"]],
        on="Race Name",
        how="left"
    )

    # Convert race date and extract year
    df['Race Date'] = pd.to_datetime(df['Race Date'], format='%Y - %B %d', errors='coerce')
    df['Year'] = df['Race Date'].dt.year

    # Convert numeric and time columns
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    for col in time_cols:
        df[col] = pd.to_timedelta(df[col], errors="coerce")

    # Clean Division values
    df["Division"] = df["Division"].astype(str).fillna("")
    df = df[df["Division"].str.startswith(("M", "F"))]

    # Patch missing ranks (where Gender & Overall rank are both missing)
    mask = df[['Gender Rank', 'Overall Rank']].isna().all(axis=1)
    df.loc[mask, 'Overall Rank'] = df.loc[mask, 'Div Rank']
    df.loc[mask, 'Div Rank'] = None

    # Add Gender column based on Division prefix
    df["Gender"] = df["Division"].apply(
        lambda x: "Male" if x.startswith("M") else ("Female" if x.startswith("F") else "Unknown")
    )

    # Remove entries with zero duration (invalid results)
    df = df[df["Bike Time"] > pd.Timedelta(0)]
    df = df[df["Run Time"] > pd.Timedelta(0)]
    df = df[df["Finish Time"] > pd.Timedelta(0)]

    # -------------------------------
    # Save Outputs
    # -------------------------------

    cleaned_dir = "data/results/cleaned"
    os.makedirs(cleaned_dir, exist_ok=True)

    parquet_path = f"{cleaned_dir}/cleaned_races_{label}.parquet"
    csv_path = f"{cleaned_dir}/cleaned_races_{label}.csv"

    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)

    print(f"✅ Cleaned and saved to: {csv_path}")
