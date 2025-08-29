import streamlit as st
import pandas as pd
from database.db import fetch_vendors, update_usage ,update_fuel
import time
import random

fuel_levels = {}

from math import radians, sin, cos, asin, sqrt
from functools import lru_cache

try:
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except Exception:
    GEOPY_AVAILABLE = False

FALLBACK_COORDS = {
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "gurgaon": (28.4595, 77.0266),
    "noida": (28.5355, 77.3910),
    "mumbai": (19.0760, 72.8777),
    "navi mumbai": (19.0330, 73.0297),
    "pune": (18.5204, 73.8567),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "vellore": (12.9165, 79.1325),
    "hyderabad": (17.3850, 78.4867),
    "kolkata": (22.5726, 88.3639),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "coimbatore": (11.0168, 76.9558),
    "madurai": (9.9252, 78.1198),
    "kochi": (9.9312, 76.2673)
}

@lru_cache(maxsize=256)
def geocode_cached(query: str):
    """
    Cached geocoder. Tries geopy (if installed) then fallback dict.
    Returns (lat, lon) or None.
    """
    if not query:
        return None
    q = query.strip()
    if not q:
        return None

    key = q.lower()
    if key in FALLBACK_COORDS:
        return FALLBACK_COORDS[key]

    if GEOPY_AVAILABLE:
        try:
            geolocator = Nominatim(user_agent="rental_view_app")
            loc = geolocator.geocode(q, timeout=5)
            if loc:
                return (loc.latitude, loc.longitude)
        except Exception:
            pass

    if "," in q:
        parts = [p.strip().lower() for p in q.split(",")]
        for p in parts:
            if p in FALLBACK_COORDS:
                return FALLBACK_COORDS[p]

    return None

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c


def simulate_fuel_updates():
    rented_vendors = fetch_vendors(filter_by="Rented")
    rented_ids = [row[0] for row in rented_vendors]

    for eq_id in rented_ids:
        if eq_id not in fuel_levels:
            fuel_levels[eq_id] = random.randint(200, 250)

        fuel_levels[eq_id] -= random.randint(5, 15)

        if fuel_levels[eq_id] <= 5:
            fuel_levels[eq_id] = random.randint(200, 250)

        conn = fetch_vendors()
        update_fuel(eq_id, fuel_levels[eq_id])

def simulate_usage_updates():
    rented_vendors = fetch_vendors(filter_by="Rented")
    rented_ids = [row[0] for row in rented_vendors]

    if not rented_ids:
        return

    eq_id = random.choice(rented_ids)
    engine_hours = round(random.uniform(1.0, 3.0), 2)
    idle_hours = round(random.uniform(0.0, 0.5), 2)

    update_usage(eq_id, engine_hours, idle_hours)

def rental_view():
    st.header("📊 View Rentals")
    
    filter_option = st.selectbox("Filter By", ["All", "Available", "Rented"])
    site_id = st.text_input("Filter by Site ID (optional)")

    # --- NEW: toggle the location section ---
    show_loc_view = st.toggle("📍 Show Location Distance View", value=False, help="Sort rented equipment by proximity to a reference location")

    table_placeholder = st.empty()

    # UI for Location Distance View (appears when toggled)
    if show_loc_view:
        st.subheader("📍 Location Distance View")
        st.caption("Choose a reference place (e.g., 'Vellore', 'Chennai', 'Delhi' or any valid city/address). We'll sort rented equipment by distance to this place.")

        # Build suggestions from current rented locations
        rented_rows = fetch_vendors(filter_by="Rented")
        rented_locations = sorted({r[10] for r in rented_rows if r[10]})  # index 10 = Location in your schema

        ref_loc = st.selectbox(
            "Reference Location",
            options=["(type a custom location)"] + rented_locations,
            index=0,
            help="Pick from current locations or choose the first option and type a custom place below."
        )

        custom_ref = ""
        if ref_loc == "(type a custom location)":
            custom_ref = st.text_input("Type a custom reference location", placeholder="e.g., Vellore, Chennai, Delhi")

        ref_query = custom_ref if custom_ref.strip() else (ref_loc if ref_loc != "(type a custom location)" else "")

        ref_coords = geocode_cached(ref_query) if ref_query else None
        if not ref_coords and ref_query:
            st.warning(f"Couldn’t geocode '{ref_query}'. Try a simpler city name, or add it to FALLBACK_COORDS in code.")
        elif not ref_query:
            st.info("Enter or select a reference location to compute distances.")

    # main live loop
    while True:
        simulate_fuel_updates()
        simulate_usage_updates()

        # base table
        if filter_option == "All":
            data = fetch_vendors(site_id=site_id if site_id else None)
        else:
            data = fetch_vendors(filter_by=filter_option, site_id=site_id if site_id else None)

        df = pd.DataFrame(data, columns=[
            "EquipmentID", "Type", "SiteID", "CheckOutDate", "CheckInDate",
            "EngineHourDay", "IdleHourDay", "OperatingDays", "DaysLeft", "Fuel",
            "Location", "Availability", "RentalType", "ReadyToShare", "SharedBySiteID"
        ])

        # --- if the Location Distance View is on, show a separate sorted table for RENTED only ---
                # --- if the Location Distance View is on, show a sorted table for RENTED only ---
        if show_loc_view:
            df_rented = df[df["Availability"] == "Rented"].copy()
            if not df_rented.empty:
                if ref_coords:
                    # compute distance for each row
                    distances = []
                    for loc in df_rented["Location"].fillna(""):
                        coords = geocode_cached(loc) if loc else None
                        if coords:
                            d = haversine_km(ref_coords[0], ref_coords[1], coords[0], coords[1])
                        else:
                            d = None
                        distances.append(d)
                    df_rented["Distance_km"] = distances
                    # sort with None at bottom
                    df_rented = df_rented.sort_values(
                        by=["Distance_km", "EquipmentID"],
                        ascending=[True, True],
                        na_position="last"
                    )
                    # ✅ replace the existing table, not create a new one
                    table_placeholder.dataframe(df_rented, use_container_width=True)
                else:
                    # no reference yet — show rented list without sorting
                    table_placeholder.dataframe(df_rented, use_container_width=True)
            else:
                table_placeholder.dataframe(df_rented, use_container_width=True)
        else:
            # normal table view
            table_placeholder.dataframe(df, use_container_width=True)


        time.sleep(2)
