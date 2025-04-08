# 🏊🚴🏃 IRONMAN Races Analysis

A complete data pipeline and dashboard to scrape, clean, and analyze IRONMAN & IRONMAN 70.3 athlete race results — including World Championship (WC) qualification tracking and performance insights.

---

## 📌 What This Project Does

- ✅ Scrapes all global IRONMAN races and result pages using Selenium  
- ✅ Extracts athlete performance data by race, division, and year  
- ✅ Cleans and standardizes results into tidy datasets  
- ✅ Identifies qualified athletes who competed at WC events  
- ✅ Offers a ready-to-deploy interactive dashboard (Streamlit or Dash)

---

## 📁 Project Structure

```
ironman_races_analysis/
├── data/
│   ├── results/
│   │   ├── races/              # Raw race result CSVs
│   │   ├── wc/                 # Raw World Championship result CSVs
│   │   ├── combined/           # Merged race + WC result files
│   │   └── cleaned/            # Final cleaned datasets
│   ├── urls/                   # Race metadata (e.g. all_ironman_races.csv)
│   └── qualified_athletes/     # Final filtered WC qualifiers
│
├── scripts/
│   ├── scrape_races.py
│   ├── scrape_results.py
│   ├── combine_race_results.py
│   ├── clean_race_results.py
│   └── calculate_wc_qualifiers.py
│
│
├── dashboard/                  # Streamlit dashboard app
│   ├── Overall_Statistics.py                  # Main entry point
│   └── pages/                  # Subpages (auto-loaded by Streamlit)
│       ├── 1_WC_Statistics.py
│       ├── 2_Best_Performances.py
│       ├── 3_Top_10_Fast_and_Brutal.py
│       └── 4_WC_Slots.py
│  
├── requirements.txt
├── .gitignore
├── README.md
└── run_all.sh                  # Optional: shell script to run full pipeline
```

---

## 🚀 Quick Start

### 1. Clone the Repo
```bash
git clone https://github.com/your-username/ironman_races_analysis.git
cd ironman_races_analysis
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔁 Full Data Pipeline

Run each script in this order to scrape, combine, and clean the data:

```bash
python scripts/scrape_races.py
python scripts/scrape_results.py
python scripts/combine_race_results.py
python scripts/clean_race_results.py
python scripts/calculate_wc_qualifiers.py
```

> Optionally, run all at once with: `bash run_all.sh` (if added)

---

## 📊 Dashboard (Optional)

Explore the results visually with the dashboard app:

```bash
streamlit run dashboard/Overall_Statistics.py
```

---

## 🔍 Use Cases

- Analyze athlete performance across different races and years  
- Track qualification pipelines into IRONMAN World Championships  
- Compare gender/division-based trends  
- Support content creation or storytelling for the endurance sports community

---

## 🤝 Contributions Welcome!

If you have suggestions, bug fixes, or want to help expand the dashboard, feel free to fork the repo and open a pull request!

---

## 📄 License

MIT License (or specify your own)
