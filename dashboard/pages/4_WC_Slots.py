import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic

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

@st.cache_data
def load_slots():
    slot_path = "https://drive.google.com/uc?export=download&id=1P45pt4A1-mB9q35JhErz-swZ6UM-JbcG"
    slots = pd.read_csv(slot_path)
    return slots

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

# Function to get multiple location suggestions using Nominatim API
def get_location_suggestions(query, limit=5):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": limit,
        "addressdetails": 1
    }
    headers = {"User-Agent": "ironman-dashboard"}
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Geocoding error: {e}")
    return []

# Load and filter race data
data = load_data()
races = load_races().dropna(subset=["Latitude", "Longitude"])
slots = load_slots()

# Filters Section
st.sidebar.header("Filters")

# Race Type Filter
race_type = sorted(slots["Race Type"].dropna().unique())
selected_race_type = st.sidebar.selectbox("Select a Race Type", race_type, index=0)
slots = slots[slots["Race Type"] == selected_race_type]

# Division Type Filter
division = sorted(slots["Division"].dropna().unique())
selected_division = st.sidebar.selectbox("Select a Division", division, index=0)
slots = slots[slots["Division"] == selected_division]

# WC Date Filter
wc_date = sorted(slots["WC Race Date"].dropna().unique(), reverse=True)
selected_wc_date = st.sidebar.selectbox("Select a WC Race Date", wc_date, index=0)

# Format the date
formatted_wc_date = pd.to_datetime(selected_wc_date, errors='coerce').strftime('%d %b %Y')  # e.g., 12 Sep 2012

slots = slots[slots["WC Race Date"] == selected_wc_date]










# Sidebar input for place
st.sidebar.header("Find Races Near a Place")
place_input = st.sidebar.text_input("Enter a place (e.g. 'Nice, France', 'Barcelona')", value="")

user_lat = user_lon = None
selected_location = None

if place_input:
    suggestions = get_location_suggestions(place_input)

    if suggestions:

        # Create a mapping of unique display names to suggestions
        unique_suggestions = {}
        for s in suggestions:
            label = s['display_name']
            if label not in unique_suggestions:
                unique_suggestions[label] = s

        # Display dropdown with unique options
        suggestion_labels = list(unique_suggestions.keys())
        selected_label = st.sidebar.selectbox("Select a location", suggestion_labels)
        selected_location = unique_suggestions[selected_label]

        if selected_location:
            user_lat = float(selected_location["lat"])
            user_lon = float(selected_location["lon"])
            st.sidebar.success(f"Selected: {selected_location['display_name']}")
    else:
        st.sidebar.warning("Could not find any matching locations.")

# Distance slider
max_distance_km = st.sidebar.slider("Search Radius (km)", min_value=50, max_value=10000, value=500, step=50)


if user_lat and user_lon:
    user_coord = (user_lat, user_lon)
    races["Distance (km)"] = races.apply(
        lambda row: geodesic(user_coord, (row["Latitude"], row["Longitude"])).km,
        axis=1
    )

    filtered_races = races[races["Distance (km)"] <= max_distance_km].copy()
    filtered_races = filtered_races.sort_values("Distance (km)")

    race_names_nearby = filtered_races["Race Name"].unique()
    filtered_slots = slots[slots["Race Name"].isin(race_names_nearby)]


    st.title("Slots Near You")
    st.markdown(f"Showing races within **{max_distance_km} km** of **{selected_location['display_name']}**")
    st.subheader(f" {selected_division} Slots for {selected_race_type} World Championship on {formatted_wc_date}")

    # Add a column that counts total athletes (slots) per Race + Division
    filtered_slots["Slot Count"] = filtered_slots.groupby(["Race Name", "Division"])["Finish Time"].transform("count")

    # Get the slowest qualifying time (max) per Race Name + Division
    slot_table = (
        filtered_slots.sort_values("Finish Time", ascending=False)
        .groupby(["Race Name", "Division", "Slot Count"], as_index=False)
        .first()
    )

    # Format the finish time for display
    slot_table["Formatted Time"] = pd.to_timedelta(slot_table["Finish Time"]).apply(format_timedelta)

    # Merge to bring in Distance (km) from filtered_races
    slot_table = pd.merge(
        slot_table,
        filtered_races[["Race Name", "Distance (km)"]],
        on="Race Name",
        how="left"
    )

    # Round distance for clean display
    slot_table["Distance (km)"] = slot_table["Distance (km)"].round(1)

    # Final columns to show
    slot_table = slot_table.rename(columns={
        "Formatted Time": "Cutoff Time",
        "Slot Count": "Slots Awarded"
    })[["Race Name", "Cutoff Time", "Slots Awarded", "Distance (km)"]]

    # Sort from slowest to fastest
    slot_table = slot_table.sort_values("Cutoff Time", ascending=False)

    # Display table
    st.dataframe(slot_table.reset_index(drop=True))



else:

    # --- Build Slot Summary Table ---
    # Add Slot Count per Race + Division
    slots["Slot Count"] = slots.groupby(["Race Name", "Division"])["Finish Time"].transform("count")

    # Get the slowest qualifying time (max) per Race Name + Division
    slot_table = (
        slots.sort_values("Finish Time", ascending=False)
        .groupby(["Race Name", "Division", "Slot Count"], as_index=False)
        .first()
    )

    # Format Finish Time
    slot_table["Formatted Time"] = pd.to_timedelta(slot_table["Finish Time"]).apply(format_timedelta)




    # Rename columns for clarity
    slot_table = slot_table.rename(columns={
        "Formatted Time": "Cutoff Time",
        "Slot Count": "Slots Awarded"
    })[["Race Name", "Division", "Cutoff Time", "Slots Awarded"]]

    # Sort from slowest to fastest cutoff time
    slot_table["Cutoff Seconds"] = pd.to_timedelta(slot_table["Cutoff Time"]).dt.total_seconds()
    slot_table = slot_table.sort_values("Cutoff Seconds", ascending=False).drop(columns="Cutoff Seconds")

    # Display the final table
    st.subheader(f" {selected_division} Slots for {selected_race_type} World Championship on {formatted_wc_date}")


    st.dataframe(slot_table.reset_index(drop=True))