import streamlit as st
from database.db import init_db
from modules.rental_form import rental_form
from modules.rental_view import rental_view

# Initialize DB
init_db()

st.sidebar.title("Rental Dashboard")
option = st.sidebar.radio("Choose Action", ["View", "Add"])

if option == "View":
    rental_view()
elif option == "Add":
    rental_form()
