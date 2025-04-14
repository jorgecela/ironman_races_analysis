import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from Parquet
@st.cache_data
def load_data():
    data_path = "https://drive.google.com/uc?export=download&id=1k3Trhg6lI6_SAvLaPP7b-t2UhtHutZ9E"
    data = pd.read_parquet(data_path)
    return data

@st.cache_data
def load_races():
    race_path = "https://drive.google.com/uc?export=download&id=1XbgeVdOjk_ocPFm9Md0fCyIy4nQ7C92C"
    races = pd.read_csv(race_path)
    return races

# Helper function to format timedelta into hh:mm:ss or mm:ss
def format_timedelta(td):
    if pd.isnull(td):
        return None
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"  # hh:mm:ss
    else:
        return f"{minutes:02}:{seconds:02}"  # mm:ss

# Dictionary of shortened races by year
shortened_races_by_year = {
    "IRONMAN 70.3 Aix-en-Provence": [2011,2016],
    "IRONMAN 70.3 Alcúdia-Mallorca": [2021],
    "IRONMAN 70.3 Cartagena": [2016],
    "IRONMAN 70.3 Chattanooga": [2017, 2018, 2019],
    "IRONMAN 70.3 Coeur d'Alene": [2024],
    "IRONMAN 70.3 Cozumel": [2016],
    "IRONMAN 70.3 Des Moines": [2021],
    "IRONMAN 70.3 Dubai": [2016],
    "IRONMAN 70.3 Durban": [2016],
    "IRONMAN 70.3 Eagleman": [2019],
    "IRONMAN 70.3 Erkner Berlin-Brandenburg": [2024],
    "IRONMAN 70.3 Florianópolis": [2024],
    "IRONMAN 70.3 Gulf Coast": [2017, 2022],
    "IRONMAN 70.3 Hawaii": [2024],
    "IRONMAN 70.3 Jonkoping European Championship": [2021, 2024],
    "IRONMAN 70.3 Kenting": [2024],
    "IRONMAN 70.3 Knokke-Heist, Belgium": [2023],
    "IRONMAN 70.3 Lapu-Lapu": [2018],
    "IRONMAN 70.3 Luxembourg Remich-Région Moselle": [2016, 2017, 2021],
    "IRONMAN 70.3 Maine": [2023],
    "IRONMAN 70.3 Melbourne": [2023],
    "IRONMAN 70.3 Middle East Championship Bahrain": [2015, 2018, 2019],
    "IRONMAN 70.3 Mont Tremblant": [2024],
    "IRONMAN 70.3 Muskoka": [2018],
    "IRONMAN 70.3 Musselman": [2022],
    "IRONMAN 70.3 New York": [2023],
    "IRONMAN 70.3 Punta del Este": [2015, 2016, 2019],
    "IRONMAN 70.3 Santa Cruz": [2017, 2023],
    "IRONMAN 70.3 Switzerland": [2024],
    "IRONMAN 70.3 Vichy": [2022],
    "IRONMAN 70.3 Victoria": [2016],
    "IRONMAN 70.3 Viet Nam": [2024],
    "IRONMAN 70.3 Waco": [2018],
    "IRONMAN 70.3 Weymouth": [2018, 2019, 2023],
    "IRONMAN 70.3 Western Australia": [2017],
    "IRONMAN Calella-Barcelona": [2021],
    "IRONMAN Cozumel": [2023],
    "IRONMAN Chattanooga": [2018, 2024],
    "IRONMAN Florida": [2014],
    "IRONMAN Hamburg European Championship": [2018],
    "IRONMAN Lake Placid": [2014],
    "IRONMAN Maryland": [2016, 2023],
    "IRONMAN New Zealand": [2012],
    "IRONMAN France Nice": [2019],
    "IRONMAN South Africa African Championship": [2019, 2021, 2022, 2023],
    "IRONMAN Switzerland Thun": [2021],
    "IRONMAN Taiwan": [2018],
    "IRONMAN Texas - North American Championship": [2016],
    "IRONMAN Vitoria-Gasteiz": [2021],
    "IRONMAN Western Australia Asia-Pacific Championship": [2017],
}
# Dictionary of current assisted races by year
current_assisted_swim = {
    "IRONMAN 70.3 Augusta": [2009, 2010, 2011,2012, 2013, 2014, 2015, 2016, 2018,2019, 2021, 2022, 2023],
    "IRONMAN 70.3 Cozumel": [2013, 2018, 2020, 2022],
    "IRONMAN 70.3 Maine": [2022, 2024],
    "IRONMAN 70.3 North Carolina": [2017, 2019, 2021, 2022, 2024],
    "IRONMAN 70.3 Oregon": [2021, 2022, 2023, 2024],
    "IRONMAN 70.3 Panama": [2012, 2013, 2014, 2016, 2023, 2024],
    "IRONMAN 70.3 Portugal - Cascais": [2022, 2023],
    "IRONMAN 70.3 Washington Tri-Cities": [2024],
    "IRONMAN Brazil": [2010,2012,2018],
    "IRONMAN California": [2022, 2023, 2024],
    "IRONMAN Chattanooga": [2014,2015,2016, 2017, 2019, 2021, 2022, 2023],
    "IRONMAN Cozumel": [2009, 2013,2015, 2016, 2017, 2018, 2019,2020, 2021, 2022, 2023, 2024],
    "IRONMAN Maryland": [2015, 2016],
    "IRONMAN Portugal - Cascais": [2023],

}

# Load data
data = load_data()
races = load_races()


# Sidebar toggle to include or exclude shortened races
st.sidebar.header("Data Filters")
exclude_shortened = st.sidebar.checkbox("Exclude Shortened Races", value=True)
exclude_curent_assisted = st.sidebar.checkbox("Exclude Current Assisted Swims", value=False)

if exclude_shortened:
    for race, years in shortened_races_by_year.items():
        data = data[~((data["Race Name"] == race) & (data["Year"].astype(int).isin(years)))]

if exclude_curent_assisted:
    for race, years in current_assisted_swim.items():
        data = data[~((data["Race Name"] == race) & (data["Year"].astype(int).isin(years)))]

# Filters Section
st.sidebar.header("Filters")

# Race Type Filter
race_type = sorted(data["Race Type"].dropna().unique())
selected_race_type = st.sidebar.selectbox("Select a Race Type", race_type, index=0)
data = data[data["Race Type"] == selected_race_type]

# Year Range Slider
min_year = int(data["Year"].min())
max_year = int(data["Year"].max())
year_range = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year), step=1)
data = data[(data["Year"] >= year_range[0]) & (data["Year"] <= year_range[1])]

# Gender Filter
genders = ["All"] + sorted(data["Gender"].dropna().unique())
selected_gender = st.sidebar.selectbox("Select a Gender", genders)
if selected_gender != "All":
    data = data[data["Gender"] == selected_gender]

# Division Filter
divisions = ["All"] + sorted(data["Division"].dropna().unique())
selected_division = st.sidebar.selectbox("Select a Division", divisions)
if selected_division != "All":
    data = data[data["Division"] == selected_division]

# Filter only finishers
data = data[data["Designation"] == "Finisher"]

# Compute average times per race
race_avg_times = data.groupby("Race Name").agg({
    "Finish Time": "mean",
    "Swim Time": "mean",
    "Bike Time": "mean",
    "Run Time": "mean"
}).reset_index()

race_avg_times = race_avg_times.merge(
    races[["Race Name", "Swim", "Bike", "Run"]],
    on="Race Name",
    how="left"
)

# Function to display top races with only the relevant column
def display_top_races(title, column, ascending=True, extra_columns=None):
    top_races = (
        race_avg_times.sort_values(by=column, ascending=ascending)
        .head(10)
        .reset_index(drop=True)
    )
    top_races.index += 1  # Start index from 1
    top_races[column] = top_races[column].apply(format_timedelta)

    display_cols = ["Race Name", column]
    if extra_columns:
        display_cols = ["Race Name"] + extra_columns + [column]

    st.subheader(title)
    st.dataframe(top_races[display_cols])

# Display tables with only the relevant columns
display_top_races("Top 10 Fastest Races (Overall)", "Finish Time", extra_columns=["Swim", "Bike", "Run"])
display_top_races("Top 10 Fastest Swim Races", "Swim Time", extra_columns=["Swim"])
display_top_races("Top 10 Fastest Bike Races", "Bike Time", extra_columns=["Bike"])
display_top_races("Top 10 Fastest Run Races", "Run Time", extra_columns=["Run"])
display_top_races("Top 10 Hardest Races (Longest Time)", "Finish Time", extra_columns=["Swim", "Bike", "Run"], ascending=False)
display_top_races("Top 10 Hardest Swim Races", "Swim Time", extra_columns=["Swim"], ascending=False)
display_top_races("Top 10 Hardest Bike Races", "Bike Time", extra_columns=["Bike"], ascending=False)
display_top_races("Top 10 Hardest Run Races", "Run Time", extra_columns=["Run"], ascending=False)