# modules/vendor_share.py
import streamlit as st
import pandas as pd
from database.db import get_flexible_rentals, set_ready_to_share

def vendor_share():
    st.title("Share Flexible Rentals")
    st.caption("Mark Flexible rentals as 'Ready to Share' so clients can see them in their dashboards.")

    df = get_flexible_rentals()

    if df.empty:
        st.info("No Flexible rentals found in the Vendor table.")
        return

    # Overview
    with st.expander("Overview", expanded=True):
        st.dataframe(
            df.sort_values(["ReadyToShare", "EquipmentID"], ascending=[True, True]).reset_index(drop=True),
            use_container_width=True
        )

    st.subheader("Mark Items Ready to Share")
    for _, row in df.iterrows():
        cols = st.columns([5, 2, 2, 2, 3])
        with cols[0]:
            st.markdown(f"**{row['EquipmentID']} – {row.get('Type','(no type)')}**")
            st.caption(f"Site: {row.get('SiteID','-')} | Location: {row.get('Location','-')} | Availability: {row.get('Availability','-')}")

        with cols[1]:
            st.metric("RentalType", row.get("RentalType","-"))

        with cols[2]:
            st.metric("Shared?", "Yes" if int(row.get("ReadyToShare",0)) == 1 else "No")

        with cols[3]:
            if int(row.get("ReadyToShare",0)) == 1:
                if st.button("Unshare", key=f"unshare_{row['EquipmentID']}"):
                    # On unshare, clear ReadyToShare and SharedBySiteID
                    set_ready_to_share(row["EquipmentID"], 0, shared_by_site_id=None)
                    st.success(f"{row['EquipmentID']} unshared.")
                    st.rerun()
            else:
                if st.button("Share", key=f"share_{row['EquipmentID']}"):
                    # On share, set ReadyToShare=1 and stamp the sharer site
                    set_ready_to_share(row["EquipmentID"], 1, shared_by_site_id=row.get("SiteID"))
                    st.success(f"{row['EquipmentID']} is now ready to share.")
                    st.rerun()

        with cols[4]:
            with st.popover("Details"):
                st.json({k: row[k] for k in row.index if k not in ["ReadyToShare"]})
