# modules/client_dashboard.py
import pandas as pd
import streamlit as st
from database.db import get_connection
from database.db import add_rental_request

def client_dashboard(site_id: int, title: str = "Client Dashboard"):
    st.title(title)

    # ---- Fetch data ----
    with get_connection() as conn:
        # Owned by this client (by SiteID)
        owned_df = pd.read_sql_query(
            """
            SELECT EquipmentID, Type, SiteID, Location, Availability, RentalType, ReadyToShare
            FROM Vendor
            WHERE SiteID = ?
            ORDER BY EquipmentID
            """,
            conn, params=(site_id,)
        )

        # All items marked ReadyToShare by any site (global share)
        shared_df = pd.read_sql_query(
            """
            SELECT EquipmentID, Type, SiteID, Location, Availability, RentalType
            FROM Vendor
            WHERE ReadyToShare = 1
            ORDER BY EquipmentID
            """,
            conn
        )

    # ✅ Your equipment ready to rent (your own items with ReadyToShare = 1)
    if owned_df.empty:
        ready_df = owned_df  # empty
    else:
        tmp = owned_df.copy()
        if "ReadyToShare" in tmp.columns:
            tmp["ReadyToShare"] = tmp["ReadyToShare"].fillna(0).astype(int)
        else:
            tmp["ReadyToShare"] = 0
        ready_df = tmp[tmp["ReadyToShare"] == 1]

    # ✅ Shared equipment from *other* clients only
    other_shared_df = shared_df[shared_df["SiteID"] != site_id] if not shared_df.empty else shared_df

    # ---- KPIs ----
    left, mid, right = st.columns(3)
    with left:
        st.metric("Your equipment (total)", len(owned_df))
    with mid:
        st.metric("Your equipment ready to rent", len(ready_df))
    with right:
        st.metric("Shared by others", len(other_shared_df))

    # ---- Section: Equipment owned by this client ----
    st.subheader("Your Equipment (owned by this client)")
    if owned_df.empty:
        st.info("You don't own any equipment yet.")
    else:
        filt_col = st.selectbox("Filter by availability", ["All", "Available", "Rented"], index=0)
        show_df = owned_df
        if filt_col != "All":
            show_df = owned_df[owned_df["Availability"].str.upper() == filt_col.upper()]
        st.dataframe(show_df.reset_index(drop=True), use_container_width=True)

    # ---- Section: Your equipment ready to rent ----
    st.subheader("Your Equipment Ready to Rent")
    if ready_df.empty:
        st.info("None of your equipment is marked ReadyToShare yet.")
    else:
        st.dataframe(ready_df.reset_index(drop=True), use_container_width=True)

    # ---- Section: Equipment on Share (from other clients) ----
    st.subheader("Equipment on Share (from other clients)")
    if other_shared_df.empty:
        st.info("No shared items from other clients.")
    else:
        for _, row in other_shared_df.iterrows():
            with st.expander(f"Equipment {row['EquipmentID']} ({row['Type']})", expanded=False):
                st.write(f"Owner Site: {row['SiteID']}, Location: {row['Location']}")

                # Use a FORM — no outer st.button
                form_key = f"req_form_{row['EquipmentID']}"
                with st.form(form_key, clear_on_submit=True):
                    req_location = st.text_input("Enter desired location", key=f"loc_{row['EquipmentID']}")
                    time_from = st.text_input("Time From (e.g. 2025-09-01 10:00)", key=f"from_{row['EquipmentID']}")
                    time_to = st.text_input("Time To (e.g. 2025-09-01 18:00)", key=f"to_{row['EquipmentID']}")
                    submitted = st.form_submit_button(f"Request {row['EquipmentID']}")

                if submitted:
                    try:
                        from database.db import add_rental_request
                        # DO NOT pass owner_site_id; your function looks it up
                        add_rental_request(
                            equipment_id=row["EquipmentID"],
                            requester_site_id=site_id,
                            location=req_location,
                            time_from=time_from,
                            time_to=time_to
                        )
                        st.success("Request sent to owner!")
                        st.rerun()  # refresh UI to reflect change
                    except Exception as e:
                        st.error(f"Could not send request: {e}")



    # ---- Section: Incoming Requests for Your Equipment ----
    # modules/client_dashboard.py (inside client_dashboard)

    from database.db import get_requests_for_owner, approve_request,update_request_status

    st.subheader("Incoming Requests for Your Equipment")
    incoming_df = get_requests_for_owner(site_id)

    if incoming_df.empty:
        st.info("No pending requests.")
    else:
        for _, row in incoming_df.iterrows():
            with st.expander(f"Request {row['RequestID']} for Equipment {row['EquipmentID']}"):
                st.write(f"**Requester Site:** {row['RequesterSiteID']}")
                st.write(f"**Requested Location:** {row['Location']}")
                st.write(f"**From:** {row['TimeFrom']}")
                st.write(f"**To:** {row['TimeTo']}")
                st.write(f"**Status:** {row['Status']}")

                # Accept / Reject buttons
                c1, c2 = st.columns(2)
                # with c1:
                #     if st.button("✅ Approve", key=f"approve_{row['RequestID']}"):
                #         update_request_status(row["RequestID"], "Approved")
                #         st.success(f"Request {row['RequestID']} approved.")
                #         st.rerun()
                # with c2:
                #     if st.button("❌ Reject", key=f"reject_{row['RequestID']}"):
                #         update_request_status(row["RequestID"], "Rejected")
                #         st.error(f"Request {row['RequestID']} rejected.")
                #         st.rerun()
                with c1:
                    if st.button("✅ Approve", key=f"approve_{row['RequestID']}"):
                        update_request_status(row["RequestID"], "Approved", row["RequesterSiteID"])
                        st.success(f"Request {row['RequestID']} approved.")
                        st.rerun()
                with c2:
                    if st.button("❌ Reject", key=f"reject_{row['RequestID']}"):
                        update_request_status(row["RequestID"], "Rejected", row["RequesterSiteID"])
                        st.error(f"Request {row['RequestID']} rejected.")
                        st.rerun()