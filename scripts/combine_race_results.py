"""
combine_race_results.py

────────────────────────────────────────────────────────────────────────────
📊 Combine IRONMAN Race & World Championship (wc) Results
────────────────────────────────────────────────────────────────────────────

🔍 What It Does:
---------------
1. Combines all CSV files from two directories:
   - General races → `data/results/races/`
   - World Championships → `data/results/wc/`
2. Saves each group as a single combined file.
3. Merges both groups into a master combined dataset.

📁 Input Directories:
---------------------
- `data/results/races/` → Individual general race result CSVs
- `data/results/wc/`    → Individual wc race result CSVs

📤 Output Files:
----------------
- `data/results/combined/all_races_combined.csv`
- `data/results/combined/all_races_wc_combined.csv`
- `data/results/combined/all_races_and_wc_combined.csv`

────────────────────────────────────────────────────────────────────────────
"""

import os
import pandas as pd

# -------------------------------
# Helper: Combine CSVs in a Folder
# -------------------------------

def combine_csvs_from_directory(input_dir):
    """
    Combines all .csv files in the given directory into a single DataFrame.
    """
    combined_data = []
    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            file_path = os.path.join(input_dir, file)
            df = pd.read_csv(file_path, low_memory=False)
            combined_data.append(df)
    return pd.concat(combined_data, ignore_index=True) if combined_data else pd.DataFrame()

# -------------------------------
# Step 1: Combine General Race Results
# -------------------------------

races_dir = "data/results/races"
combined_races = combine_csvs_from_directory(races_dir)

races_output_path = "data/results/combined/all_races_combined.csv"
combined_races.to_csv(races_output_path, index=False)
print(f"✅ General race data combined and saved to '{races_output_path}'")

# -------------------------------
# Step 2: Combine wc Race Results
# -------------------------------

wc_dir = "data/results/wc"
combined_wc = combine_csvs_from_directory(wc_dir)

wc_output_path = "data/results/combined/all_races_wc_combined.csv"
combined_wc.to_csv(wc_output_path, index=False)
print(f"✅ WC race data combined and saved to '{wc_output_path}'")

# -------------------------------
# Step 3: Merge Both Groups Into Final Dataset
# -------------------------------

final_combined = pd.concat([combined_races, combined_wc], ignore_index=True)

final_output_path = "data/results/combined/all_races_and_WC_combined.csv"
final_combined.to_csv(final_output_path, index=False)
print(f"🎉 All race + wc data combined and saved to '{final_output_path}'")
