import streamlit as st
import pandas as pd
from database.db import fetch_vendors

def rental_view():
    st.header("📊 View Rentals")

    filter_option = st.selectbox("Filter By", ["All", "Available", "Rented"])
    site_id = st.text_input("Filter by Site ID (optional)")

    if filter_option == "All":
        data = fetch_vendors(site_id=site_id if site_id else None)
    else:
        data = fetch_vendors(filter_by=filter_option, site_id=site_id if site_id else None)

    df = pd.DataFrame(data, columns=[
        "EquipmentID", "Type", "SiteID", "CheckOutDate", "CheckInDate",
        "EngineHourDay", "IdleHourDay", "OperatingDays", "DaysLeft",
        "Fuel", "Location", "Availability", "RentalType"
    ])

    # ✅ Make view wider
    st.dataframe(df, use_container_width=True)
