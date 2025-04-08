"""
calculate_wc_qualifiers.py

────────────────────────────────────────────────────────────────────────────
🏁 Identify and Filter IRONMAN WC Qualifiers from Race Results
────────────────────────────────────────────────────────────────────────────

🔍 What It Does:
---------------
This script identifies athletes who likely qualified for an IRONMAN or
IRONMAN 70.3 World Championship (WC) by analyzing historical race data
and matching athletes who later raced at a WC event.

📗 Key Logic Steps:
-------------------
1. Load and clean race + WC result datasets
2. Match athletes across qualifying + WC races
3. Filter by finish status, valid divisions, and season eligibility
4. Calculate time gaps between qualifying and WC races
5. Keep only the most statistically common (mode) time gaps per gender
6. Remove duplicates, keeping only top-ranked results

📥 Input:
--------
- `cleaned_races_data.csv` → All races
- `cleaned_races_wc.csv`    → WC races only

📤 Output:
---------
- `qualified_athletes.csv` → Cleaned, matched, deduplicated qualifiers

────────────────────────────────────────────────────────────────────────────
"""

import pandas as pd

# -------------------------------
# Qualifying Season Cutoffs (for 2025)
# -------------------------------

qualifying_start_70_3 = pd.to_datetime("07/07/2024", format="%d/%m/%Y")
qualifying_start_IM = pd.to_datetime("18/08/2024", format="%d/%m/%Y")

# -------------------------------
# Load Data
# -------------------------------

race_results = pd.read_csv("data/results/cleaned/cleaned_races_data.csv")
wc_results = pd.read_csv("data/results/cleaned/cleaned_races_wc.csv")

# Convert dates and times
race_results["Race Date"] = pd.to_datetime(race_results["Race Date"])
wc_results["Race Date"] = pd.to_datetime(wc_results["Race Date"])
race_results["Finish Time"] = pd.to_timedelta(race_results["Finish Time"])
wc_results["Finish Time"] = pd.to_timedelta(wc_results["Finish Time"])

# -------------------------------
# Filter Valid Race Types
# -------------------------------

valid_race_types = ["IRONMAN", "IRONMAN 70.3"]
race_results = race_results[race_results["Race Type"].isin(valid_race_types)]
wc_results = wc_results[wc_results["Race Type"].isin(valid_race_types)]

# -------------------------------
# Match Athletes Across Datasets
# -------------------------------

qualified_athletes = race_results.merge(
    wc_results[['Athlete', 'Division', 'Race Type', 'Race Date']],
    on=['Athlete', 'Division', 'Race Type'],
    how='inner'
)

# Clean division & keep gendered ones only
qualified_athletes["Division"] = qualified_athletes["Division"].astype(str).fillna("")
qualified_athletes = qualified_athletes[qualified_athletes["Division"].str.startswith(("M", "F"))]

# Qualifying race must precede WC race
qualified_athletes = qualified_athletes[
    qualified_athletes["Race Date_x"] < qualified_athletes["Race Date_y"]
]

# Rename dates for clarity
qualified_athletes.rename(columns={
    "Race Date_x": "Qualifying Race Date",
    "Race Date_y": "WC Race Date"
}, inplace=True)

# -------------------------------
# Apply Additional Filters
# -------------------------------

# Only include finishers
qualified_athletes = qualified_athletes[qualified_athletes["Designation"] == "Finisher"]

# Remove races from the current qualifying season
qualified_athletes = qualified_athletes[
    ((qualified_athletes["Race Type"] == "IRONMAN 70.3") &
     (qualified_athletes["Qualifying Race Date"] < qualifying_start_70_3)) |
    ((qualified_athletes["Race Type"] == "IRONMAN") &
     (qualified_athletes["Qualifying Race Date"] < qualifying_start_IM))
]

# -------------------------------
# Time Gap Analysis
# -------------------------------

qualified_athletes["Original Index"] = qualified_athletes.index  # Preserve order
qualified_athletes["Time Gap"] = (
    qualified_athletes["WC Race Date"] - qualified_athletes["Qualifying Race Date"]
).dt.days

# Keep closest qualifying race per athlete-WC pair
closest_race_idx = (
    qualified_athletes
    .groupby(["Athlete", "Race Name", "Qualifying Race Date"])["Time Gap"]
    .idxmin()
)
qualified_athletes = qualified_athletes.loc[closest_race_idx]

# -------------------------------
# Filter Using Most Common Time Gap by Gender
# -------------------------------

# Add gender column
qualified_athletes["Gender"] = qualified_athletes["Division"].apply(
    lambda x: "Male" if x.startswith("M") else "Female"
)

# Get mode Time Gap per race and gender
most_common_time_gaps = (
    qualified_athletes
    .groupby(["Qualifying Race Date", "Race Name", "Race Type", "Gender"])["Time Gap"]
    .agg(lambda x: x.mode()[0] if not x.mode().empty else None)
    .reset_index()
    .rename(columns={"Time Gap": "Most Common Time Gap"})
)

# Merge and filter outliers
qualified_athletes = qualified_athletes.merge(
    most_common_time_gaps,
    on=["Qualifying Race Date", "Race Name", "Race Type", "Gender"],
    how="left"
)
qualified_athletes = qualified_athletes[
    qualified_athletes["Time Gap"] == qualified_athletes["Most Common Time Gap"]
]
qualified_athletes.drop(columns=["Most Common Time Gap"], inplace=True)

# -------------------------------
# Deduplicate: Best Ranked Result
# -------------------------------

qualified_athletes["Div Rank"] = pd.to_numeric(qualified_athletes["Div Rank"], errors="coerce")
qualified_athletes["Overall Rank"] = pd.to_numeric(qualified_athletes["Overall Rank"], errors="coerce")

qualified_athletes = (
    qualified_athletes
    .sort_values(by=["Div Rank", "Overall Rank"], ascending=True)
    .groupby(["Athlete", "WC Race Date"])
    .head(1)
)

# Restore original order
qualified_athletes = qualified_athletes.sort_values(by="Original Index")
qualified_athletes.drop(columns=["Original Index"], inplace=True)
qualified_athletes.reset_index(drop=True, inplace=True)

# -------------------------------
# Save Output
# -------------------------------

output_path = "data/qualified_athletes/qualified_athletes.csv"
qualified_athletes.to_csv(output_path, index=False)
print(f"✅ Cutoff times calculated and saved to '{output_path}'")
