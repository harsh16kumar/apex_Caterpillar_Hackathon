import streamlit as st
import pandas as pd
from database.db import fetch_vendors
from geopy.distance import geodesic

location_coords = {
    'chennai': (13.0827, 80.2707),
    'Vellore': (12.9165, 79.1325),
    'delhi': (28.6139, 77.2090),
    'Mumbai': (19.0760, 72.8777),
    'Hyderabad': (17.3850, 78.4867),
}

def location_view():
    st.header("📍 Equipment by Distance from Selected Location")

    # Fetch all unique locations from the DB
    data = fetch_vendors()
    all_locations = sorted(set(row[10] for row in data if row[10]))

    selected_location = st.selectbox("Select a Location", all_locations)

    if selected_location:
        if selected_location not in location_coords:
            st.error(f"No coordinates found for {selected_location}. Please update mapping.")
            return

        selected_coord = location_coords[selected_location]

        # Compute distances
        location_distances = []
        for loc in all_locations:
            if loc not in location_coords:
                continue
            dist = geodesic(selected_coord, location_coords[loc]).kilometers
            location_distances.append((loc, dist))

        # Sort by distance
        sorted_locations = sorted(location_distances, key=lambda x: x[1])

        st.subheader("📌 Locations Sorted by Distance")
        dist_df = pd.DataFrame(sorted_locations, columns=["Location", "Distance (km)"])
        st.dataframe(dist_df, use_container_width=True)

        # Show equipment info for all locations sorted by distance
        all_data = []
        for loc, dist in sorted_locations:
            loc_data = [row for row in data if row[10] == loc]
            for row in loc_data:
                all_data.append(list(row) + [dist])

        # Display equipment info
        if all_data:
            eq_df = pd.DataFrame(all_data, columns=[
                "EquipmentID", "Type", "SiteID", "CheckOutDate", "CheckInDate",
                "EngineHourDay", "IdleHourDay", "OperatingDays", "DaysLeft",
                "Fuel", "Location", "Availability", "RentalType", "Distance (km)"
            ])
            eq_df.sort_values("Distance (km)", inplace=True)
            st.subheader("🛠️ Equipment List Sorted by Proximity")
            st.dataframe(eq_df, use_container_width=True)
        else:
            st.info("No equipment found near selected location.")
