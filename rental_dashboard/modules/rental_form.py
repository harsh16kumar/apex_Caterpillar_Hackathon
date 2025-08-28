import streamlit as st
from database.db import insert_site, get_available_types, get_available_equipment_ids, rent_equipment

def rental_form():
    st.header("➕ Add Rental Entry")

    if "step" not in st.session_state:
        st.session_state.step = 1
    if "site_info" not in st.session_state:
        st.session_state.site_info = {}
    if "selected_type" not in st.session_state:
        st.session_state.selected_type = ""   # store selected equipment type

    # -------------------------
    # STEP 1: Site Information
    # -------------------------
    if st.session_state.step == 1:
        st.subheader("Step 1: Site Information")
        site_id = st.number_input("Site ID", min_value=1)
        contact = st.text_input("Contact Details")
        site_location = st.text_input("Site Location")

        if st.button("Next ➡️"):
            if site_id and contact and site_location:
                insert_site(site_id, site_location, contact)
                st.session_state.site_info = {
                    "site_id": site_id,
                    "contact": contact,
                    "location": site_location
                }
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("⚠️ Please fill all fields before proceeding.")

    # -------------------------
    # STEP 2: Equipment Information
    # -------------------------
    elif st.session_state.step == 2:
        st.subheader("Step 2: Equipment Information")
        site_id = st.session_state.site_info["site_id"]

        available_types = get_available_types()
        if not available_types:
            st.warning("❌ No available equipment left.")
            return

        # Add "" as first option
        type_ = st.selectbox(
            "Select Equipment Type",
            options=[""] + available_types,
            key="equip_type",
            index=([""] + available_types).index(st.session_state.selected_type) if st.session_state.selected_type in [""] + available_types else 0
        )

        # Store selection in session state
        st.session_state.selected_type = type_

        if type_ == "":
            st.info("ℹ️ Please select an equipment type to continue.")
        else:
            available_ids = get_available_equipment_ids(type_)
            available_count = len(available_ids)

            if available_count == 0:
                st.warning(f"❌ No {type_} available right now.")
            else:
                st.info(f"✅ {available_count} {type_}(s) available")

                with st.form("equipment_form"):
                    quantity = st.selectbox(
                        "Select Quantity",
                        options=list(range(1, available_count + 1)),
                        help="Select how many you want to rent"
                    )

                    operating_days = st.number_input("Operating Days", min_value=1)
                    equip_location = st.text_input("Equipment Location", st.session_state.site_info["location"])
                    start_date = st.date_input("Start Date")
                    rental_type = st.selectbox("Rental Type", ["Rigid", "Flexible"])

                    submitted = st.form_submit_button("📌 Rent Equipment")

                    if submitted:
                        assigned_ids = available_ids[:quantity]

                        for eq_id in assigned_ids:
                            rent_equipment(
                                equipment_id=eq_id,
                                site_id=site_id,
                                operating_days=operating_days,
                                location=equip_location,
                                start_date=str(start_date),
                                rental_type=rental_type
                            )

                        st.success(f"✅ Assigned {quantity} {type_}(s): {', '.join(map(str, assigned_ids))}")

                        # Reset selection after renting
                        st.session_state.selected_type = ""
                        st.rerun()

        if st.button("⬅️ Back to Site Info"):
            st.session_state.step = 1
            st.session_state.selected_type = ""
            st.rerun()
