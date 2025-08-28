import streamlit as st
import pandas as pd
from database.db import fetch_vendors, update_usage ,update_fuel
import time
import random

fuel_levels = {}

def simulate_fuel_updates():
    rented_vendors = fetch_vendors(filter_by="Rented")
    rented_ids = [row[0] for row in rented_vendors]

    for eq_id in rented_ids:
        # Initialize fuel if not present
        if eq_id not in fuel_levels:
            fuel_levels[eq_id] = random.randint(200, 250)  # full tank

        # Decrease fuel by a small random amount
        fuel_levels[eq_id] -= random.randint(5, 15)

        # If fuel is empty or below threshold, refill to full
        if fuel_levels[eq_id] <= 5:
            fuel_levels[eq_id] = random.randint(200, 250)

        # Update fuel in DB
        conn = fetch_vendors()  # already in DB functions, could create a separate update_fuel() function
        update_fuel(eq_id, fuel_levels[eq_id])

def simulate_usage_updates():
    rented_vendors = fetch_vendors(filter_by="Rented")
    rented_ids = [row[0] for row in rented_vendors]

    if not rented_ids:
        return

    # Pick random rented equipment
    eq_id = random.choice(rented_ids)
    engine_hours = round(random.uniform(0.1, 1.0), 2)
    idle_hours = round(random.uniform(0.0, 0.5), 2)

    update_usage(eq_id, engine_hours, idle_hours)

def rental_view():
    st.header("📊 View Rentals")
    
    filter_option = st.selectbox("Filter By", ["All", "Available", "Rented"])
    site_id = st.text_input("Filter by Site ID (optional)")

    # Placeholder for in-place updates
    table_placeholder = st.empty()

    while True:
        # Simulate fuel updates
        simulate_fuel_updates()
        simulate_usage_updates()

        # Fetch updated data
        if filter_option == "All":
            data = fetch_vendors(site_id=site_id if site_id else None)
        else:
            data = fetch_vendors(filter_by=filter_option, site_id=site_id if site_id else None)

        df = pd.DataFrame(data, columns=[
            "EquipmentID", "Type", "SiteID", "CheckOutDate", "CheckInDate",
            "EngineHourDay", "IdleHourDay", "OperatingDays", "DaysLeft",
            "Fuel", "Location", "Availability", "RentalType"
        ])

        # Update table in-place
        table_placeholder.dataframe(df, use_container_width=True)

        time.sleep(2)  # refresh every 2 seco