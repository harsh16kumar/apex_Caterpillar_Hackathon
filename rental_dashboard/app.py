# import streamlit as st
# from database.db import init_db
# from modules.rental_form import rental_form
# from modules.rental_view import rental_view
# # from modules.rental_view import rental_view
# from modules.location_view import location_view

# # Initialize DB
# init_db()

# st.sidebar.title("Rental Dashboard")
# option = st.sidebar.radio("Choose Action", ["View", "Add"])

# if option == "View":
#     rental_view()
# elif option == "Add":
#     rental_form()


import streamlit as st
from database.db import init_db, ensure_vendor_share_columns
from modules.rental_form import rental_form
from modules.rental_view import rental_view
from modules.client_dashboard import client_dashboard
from modules.analysis import demand_forecast_view
from modules.location_view import location_view  # if you use it inside vendor views
import pandas as pd
from modules.vendor_share import vendor_share

# --- App setup ---
st.set_page_config(page_title="Rental Dashboard", layout="wide")
init_db()
ensure_vendor_share_columns()

# --- Top bar: profile selector (top-left) ---
if "profile" not in st.session_state:
    st.session_state.profile = "Vendor"

top_cols = st.columns([3, 7])
with top_cols[0]:
    st.session_state.profile = st.radio(
        "Profile",
        ["Vendor", "Client 1", "Client 2"],
        index=["Vendor", "Client 1", "Client 2"].index(st.session_state.profile),
        horizontal=True
    )

profile = st.session_state.profile

if profile == "Vendor":
    st.sidebar.title("Rental Dashboard (Vendor)")
    option = st.sidebar.radio("Choose Action", ["View", "Add","Share", "Analysis"], index=0)

    if option == "View":
        rental_view()
    elif option == "Add":
        rental_form()
    elif option == "Share":
        vendor_share()  # <-- NEW
    elif option == "Analysis":
        demand_forecast_view()

elif profile == "Client 1":
    client_dashboard(site_id=1, title="Client 1 Dashboard")

elif profile == "Client 2":
    client_dashboard(site_id=2, title="Client 2 Dashboard")

