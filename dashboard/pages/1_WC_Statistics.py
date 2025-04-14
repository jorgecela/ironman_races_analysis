import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# Load data from Parquet
@st.cache_data
def load_data():
    data_path = "https://drive.google.com/uc?export=download&id=1WIa8fTSU2OvVWDq1dEnvFex_OIa4whcq"
    data = pd.read_parquet(data_path)
    return data

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

# Reasonable axis limits in hours or minutes depending on the discipline
x_axis_limits = {
    "IRONMAN World Championship": {
        "swim": (40, 140),     # in minutes
        "bike": (3.5, 9),       # in hours
        "run": (2, 8),        # in hours
        "finish": (7.5, 17)     # in hours
    },
    "IRONMAN 70.3 World Championship": {
        "swim": (18, 60),      # in minutes
        "bike": (1.8, 4.5),       # in hours
        "run": (1, 3.5),        # in hours
        "finish": (3.5, 8.5)      # in hours
    }
}

# Dictionary of shortened races by year
shortened_races_by_year = {
    "IRONMAN 70.3 Aix-en-Provence": [2011,2016],
    "IRONMAN 70.3 Alcúdia-Mallorca": [2021],
    "IRONMAN 70.3 Cartagena": [2016],
    "IRONMAN 70.3 Chattanooga": [2017, 2018, 2019],
    "IRONMAN 70.3 Coeur d'Alene": [2024],
    "IRONMAN 70.3 Costa Navarino, Peloponnese, Greece": [2024],
    "IRONMAN 70.3 Cozumel": [2016],
    "IRONMAN 70.3 Des Moines": [2021],
    "IRONMAN 70.3 Dubai": [2016],
    "IRONMAN 70.3 Durban": [2016],
    "IRONMAN 70.3 Eagleman": [2019],
    "IRONMAN 70.3 Erkner": [2024],
    "IRONMAN 70.3 Florianopolis": [2024],
    "IRONMAN 70.3 Gulf Coast": [2017, 2022],
    "IRONMAN 70.3 Hawaii": [2024],
    "IRONMAN 70.3 Jonkoping European Championship": [2021, 2024],
    "IRONMAN 70.3 Kenting": [2024],
    "IRONMAN 70.3 Knokke-Heist": [2023],
    "IRONMAN 70.3 Luxembourg": [2016, 2017, 2021],
    "IRONMAN 70.3 Maine": [2023],
    "IRONMAN 70.3 Melbourne": [2023],
    "IRONMAN 70.3 Middle East Championship Bahrain": [2015, 2018, 2019],
    "IRONMAN 70.3 Mont-Tremblant": [2024],
    "IRONMAN 70.3 Muskoka": [2018],
    "IRONMAN 70.3 Musselman": [2022],
    "IRONMAN 70.3 New York": [2023],
    "IRONMAN 70.3 Punta del Este": [2015, 2016, 2019],
    "IRONMAN 70.3 Santa Cruz": [2017, 2023],
    "IRONMAN 70.3 Switzerland": [2024],
    "IRONMAN 70.3 Vichy": [2022],
    "IRONMAN 70.3 Victoria": [2016],
    "IRONMAN 70.3 Vietnam": [2024],
    "IRONMAN 70.3 Waco": [2018],
    "IRONMAN 70.3 Weymouth": [2018, 2019, 2023],
    "IRONMAN 70.3 Western Australia": [2017],
    "IRONMAN Calella-Barcelona": [2021],
    "IRONMAN Cozumel Latin American Championship": [2023],
    "IRONMAN Chattanooga": [2018, 2024],
    "IRONMAN Florida": [2014],
    "IRONMAN Hamburg": [2018],
    "IRONMAN Lake Placid": [2014],
    "IRONMAN Maryland": [2016, 2023],
    "IRONMAN New Zealand": [2012],
    "IRONMAN France": [2019],
    "IRONMAN South Africa African Championship": [2019, 2021, 2022, 2023],
    "IRONMAN Switzerland Thun": [2021],
    "IRONMAN Taiwan": [2018],
    "IRONMAN Texas North American Championship": [2016],
    "IRONMAN Vitoria-Gasteiz": [2021],
    "IRONMAN Western Australia Asia Pacific Championship": [2017],
}
# Dictionary of current assisted races by year
current_assisted_swim = {
    "IRONMAN 70.3 Augusta": [2009, 2010, 2011,2012, 2013, 2014, 2015, 2016, 2018,2019, 2021, 2022, 2023],
    "IRONMAN 70.3 Cozumel": [2013, 2018, 2020, 2022],
    "IRONMAN 70.3 Maine": [2022, 2024],
    "IRONMAN 70.3 North Carolina": [2017, 2019, 2021, 2022, 2024],
    "IRONMAN 70.3 Oregon": [2021, 2022, 2023, 2024],
    "IRONMAN 70.3 Panama": [2012, 2013, 2014, 2016, 2023, 2024],
    "IRONMAN 70.3 Cascais Portugal": [2022, 2023],
    "IRONMAN 70.3 Washington Tri-Cities": [2024],
    "IRONMAN Brazil": [2010,2012,2018],
    "IRONMAN California": [2022, 2023, 2024],
    "IRONMAN Chattanooga": [2014,2015,2016, 2017, 2019, 2021, 2022, 2023],
    "IRONMAN Cozumel Latin American Championship": [2009, 2013,2015, 2016, 2017, 2018, 2019,2020, 2021, 2022, 2023, 2024],
    "IRONMAN Maryland": [2015, 2016],
    "IRONMAN Portugal-Cascais": [2023],

}


data = load_data()

# Sidebar toggle to include or exclude shortened races
st.sidebar.header("Data Filters")
exclude_shortened = st.sidebar.checkbox("Exclude Shortened Races", value=True)


if exclude_shortened:
    for race, years in shortened_races_by_year.items():
        data = data[~((data["Race Name"] == race) & (data["Year"].astype(int).isin(years)))]



# Filters Section
st.sidebar.header("Filters")

# Race Filter
races = sorted(data["Race Name"].dropna().unique())
selected_race = st.sidebar.selectbox("Select a Race", races, index=0)
data = data[data["Race Name"] == selected_race]

limits = x_axis_limits.get(selected_race, None)

# Year Filter
year = ["All"] + sorted(data["Year"].dropna().unique())
selected_year = st.sidebar.selectbox("Select a Year", year)
if selected_year != "All":
    data = data[data["Year"] == selected_year]

# Division Filter
divisions = ["All"] + sorted(data["Division"].dropna().unique())
selected_division = st.sidebar.selectbox("Select a Division", divisions)
if selected_division != "All":
    data = data[data["Division"] == selected_division]


# Add a title and description
st.title(f"{selected_race}: Overall Statistics")
st.markdown(
    """
    This dashboard provides insights into Ironman race results, with time-based statistics, participation trends. Use the filters to narrow down data for specific races or divisions.
    """
)


# Summary Statistics Section
st.header("Summary Statistics")
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)
total_races = data["Race Name"].nunique()
total_athletes = len(data)
unique_divisions = data["Division"].nunique()

# Filter out non-finishers for time-based statistics
finished_data = data[data["Designation"] == "Finisher"]

avg_total_time = finished_data["Finish Time"].mean()
avg_swim_time = finished_data["Swim Time"].mean()
avg_bike_time = finished_data["Bike Time"].mean()
avg_run_time = finished_data["Run Time"].mean()


with col1:
    st.metric("Total Athletes", total_athletes)

with col2:
    st.metric("Avg Finish Time", format_timedelta(avg_total_time))

with col4:
    st.metric("Avg Swim Time", format_timedelta(avg_swim_time))

with col5:
    st.metric("Avg Bike Time", format_timedelta(avg_bike_time))

with col6:
    st.metric("Avg Run Time", format_timedelta(avg_run_time))


# Histograms and Distributions
st.header("Time Distributions")


# Plot Finish Time Distribution (large plot)
st.subheader("Distribution of Finish Time")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(finished_data["Finish Time"].dt.total_seconds() / 3600, bins=30, kde=True, ax=ax)
if limits:
    ax.set_xlim(limits["finish"])
ax.set_title("Distribution of Finish Time (hours)")
ax.set_xlabel("Time (hours)")
ax.set_ylabel("Frequency")
st.pyplot(fig)

# Plot Swim, Bike, and Run Distributions (smaller plots in a row)
st.subheader("Distribution of Swim, Bike, and Run Times")

col1, col2, col3 = st.columns(3)

# Swim Time Distribution
with col1:
    st.markdown("**Swim**")
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.histplot(finished_data["Swim Time"].dt.total_seconds() / 60, bins=30, kde=True, ax=ax, color="blue")
    if limits:
        ax.set_xlim(limits["swim"])
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("")
    ax.set_title("Swim Time")
    st.pyplot(fig)

# Bike Time Distribution
with col2:
    st.markdown("**Bike**")
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.histplot(finished_data["Bike Time"].dt.total_seconds() / 3600, bins=30, kde=True, ax=ax, color="green")
    if limits:
        ax.set_xlim(limits["bike"])
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("")
    ax.set_title("Bike Time")
    st.pyplot(fig)

# Run Time Distribution
with col3:
    st.markdown("**Run**")
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.histplot(finished_data["Run Time"].dt.total_seconds() / 3600, bins=30, kde=True, ax=ax, color="red")
    if limits:
        ax.set_xlim(limits["run"])
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("")
    ax.set_title("Run Time")
    st.pyplot(fig)



# Participation Trends
st.header("Participation Trends Over Years")
participation_data = data.groupby("Year").size()
st.line_chart(participation_data)

# Performance Trends Over Years
st.header("Performance Trends Over Years")
avg_time_by_year = finished_data.groupby("Year")["Finish Time"].mean()
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(avg_time_by_year.index, avg_time_by_year.dt.total_seconds() / 3600, marker='o', linestyle='-')
ax.set_xlabel("Year")
ax.set_ylabel("Average Finish Time (hours)")
ax.set_title("Average Finish Time Trend Over Years")
st.pyplot(fig)