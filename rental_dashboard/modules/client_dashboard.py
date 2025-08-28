import streamlit as st
from database.db import init_db, fetch_vendors  # added fetch_vendors
from modules.rental_form import rental_form
from modules.rental_view import rental_view
from modules.location_view import location_view  # if you use it inside vendor views
import pandas as pd

def to_df(rows):
    """Convert rows (list of tuples) to a DataFrame with sensible headers."""
    if not rows:
        return pd.DataFrame()
    # Adjust the column names based on your actual Vendor table schema.
    # Example: (VendorID, Name, SiteID, Availability, Type, Location, ...)
    cols = ["VendorID", "Name", "SiteID", "Availability", "Type", "Location"]
    # If row width differs, expand/trim cols accordingly:
    max_len = max(len(r) for r in rows)
    if len(cols) < max_len:
        cols = cols + [f"Col{i}" for i in range(len(cols)+1, max_len+1)]
    elif len(cols) > max_len:
        cols = cols[:max_len]
    return pd.DataFrame(rows, columns=cols)

def client_dashboard(site_id: int, title: str):
    st.title(f"{title} — SiteID {site_id}")

    rows = fetch_vendors(site_id=site_id)  # pulls all equipment for that customer/site
    df = to_df(rows)

    if df.empty:
        st.warning("No records found for this site.")
        return

    # (Optional) reorder common columns if they exist
    preferred = [c for c in ["VendorID", "Name", "Type", "Availability", "RentalType", "Location", "SiteID"] if c in df.columns]
    others = [c for c in df.columns if c not in preferred]
    df = df[preferred + others]

    st.caption(f"Total equipment: {len(df)}")
    st.dataframe(df, use_container_width=True)
