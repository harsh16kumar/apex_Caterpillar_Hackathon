import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from database.db import fetch_vendors, mark_ready_to_share


# Keep keys lowercased for reliable lookups
LOCATION_COORDS = {
    "chennai":   (13.0827, 80.2707),
    "vellore":   (12.9165, 79.1325),
    "delhi":     (28.6139, 77.2090),
    "mumbai":    (19.0760, 72.8777),
    "hyderabad": (17.3850, 78.4867),
}

# Expected Vendor schema in SELECT * order
VENDOR_COLUMNS = [
    "EquipmentID", "Type", "SiteID", "CheckOutDate", "CheckInDate",
    "EngineHourDay", "IdleHourDay", "OperatingDays", "DaysLeft", "Fuel",
    "Location", "Availability", "RentalType", "ReadyToShare", "SharedBySiteID"
]

def _rows_to_df(rows: list[tuple]) -> pd.DataFrame:
    normalized = []
    for row in rows:
        r = list(row)
        while len(r) < len(VENDOR_COLUMNS):
            r.append(None)
        r = r[:len(VENDOR_COLUMNS)]
        normalized.append(r)
    return pd.DataFrame(normalized, columns=VENDOR_COLUMNS)

def _norm_loc(s: str | None) -> str | None:
    return s.strip().lower() if isinstance(s, str) else None

def location_view(current_site_id: int):
    st.header("📍 Equipment by Distance from Selected Location")

    # --- Load vendor data safely
    rows = fetch_vendors()  # must be SELECT * FROM Vendor
    df = _rows_to_df(rows)

    # Quick status/diagnostics (collapsible)
    with st.expander("Debug info", expanded=False):
        st.write("Row count:", len(df))
        st.write("Columns:", list(df.columns))
        st.write("Sample:", df.head(3))
        st.write("RentalType distribution (raw):")
        st.write(df["RentalType"].value_counts(dropna=False))

    # --- Build list of locations from DB
    db_locs = df["Location"].dropna().astype(str).map(lambda x: x.strip()).replace("", pd.NA).dropna().tolist()
    display_locations = sorted({loc: loc.title() for loc in db_locs}.values())

    coords_map = {k.lower(): v for k, v in LOCATION_COORDS.items()}

    # If DB has no locations, allow user to pick from known coords so page still works
    if not display_locations:
        st.info("No locations found in the DB. Showing known cities list instead.")
        display_locations = sorted([k.title() for k in coords_map.keys()])

    selected_display = st.selectbox("Select a Location", display_locations)
    if not selected_display:
        return
    selected_key = _norm_loc(selected_display)

    if selected_key not in coords_map:
        st.error(
            f"No coordinates found for **{selected_display}**. "
            f"Known: {', '.join(sorted(n.title() for n in coords_map.keys()))}. "
            f"Update LOCATION_COORDS."
        )
        return

    selected_coord = coords_map[selected_key]

    # Normalize every row's location and mark which ones are mappable
    df["_loc_key"] = df["Location"].map(_norm_loc)
    df["_has_coord"] = df["_loc_key"].isin(coords_map.keys())

    if not df["_has_coord"].any():
        st.warning("None of the equipment locations match your coordinate map. "
                   "They might differ by spelling/case/whitespace. "
                   "Try adding them to LOCATION_COORDS or cleaning the DB values.")
        # Still show a table so the page isn't blank
        st.dataframe(df.drop(columns=["_loc_key", "_has_coord"]), use_container_width=True)
        return

    # Compute distance per distinct location
    distinct_keys = sorted(df.loc[df["_has_coord"], "_loc_key"].dropna().unique().tolist())
    key_to_distance_km = {k: geodesic(selected_coord, coords_map[k]).kilometers for k in distinct_keys}

    # Locations sorted by distance
    st.subheader("📌 Locations Sorted by Distance")
    dist_df = pd.DataFrame([(k.title(), key_to_distance_km[k]) for k in distinct_keys],
                           columns=["Location", "Distance (km)"]).sort_values("Distance (km)")
    st.dataframe(dist_df, use_container_width=True)

    # Equipment with distance
    eq = df.loc[df["_has_coord"]].copy()
    eq["Distance (km)"] = eq["_loc_key"].map(key_to_distance_km)

    # Clean / types
    eq["SiteID"] = pd.to_numeric(eq["SiteID"], errors="coerce").astype("Int64")

    # Sort and show
    eq = eq.sort_values(["Distance (km)", "Type", "EquipmentID"], kind="stable")
    st.subheader("🛠️ Equipment List Sorted by Proximity")
    show_cols = [c for c in eq.columns if c not in ["_loc_key", "_has_coord", "SharedBySiteID"]]
    st.dataframe(eq[show_cols], use_container_width=True)

    # --- Toggle section
    st.markdown("### 🔁 Flexible Equipment — Share Toggle")
    show_only_flexible = st.checkbox("Show only flexible rentals", value=True)

    # Null/whitespace-safe filter
    rental_type_series = eq["RentalType"].fillna("").astype(str).str.strip().str.lower()
    toggles_df = eq[rental_type_series.eq("flexible")] if show_only_flexible else eq

    if toggles_df.empty:
        if show_only_flexible:
            st.info("No **Flexible** rentals in view. Uncheck filter to show all.")
        else:
            st.info("No equipment rows available for toggles.")
        return

    # Backward compatibility: Streamlit versions without st.toggle
    use_toggle = hasattr(st, "toggle")

    for _, r in toggles_df.iterrows():
        eid = str(r["EquipmentID"])
        etype = (str(r["Type"]) if pd.notna(r["Type"]) else "-")
        owner_site = int(r["SiteID"]) if pd.notna(r["SiteID"]) else None
        dist_km = float(r["Distance (km)"]) if pd.notna(r["Distance (km)"]) else None
        current_flag = bool(r["ReadyToShare"]) if pd.notna(r["ReadyToShare"]) else False

        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 3])
        with c1:
            st.write(f"**{eid}**")
        with c2:
            st.write(etype)
        with c3:
            st.write(f"Owner Site: {owner_site if owner_site is not None else '-'}")
        with c4:
            st.write(f"Distance: {dist_km:.1f} km" if dist_km is not None else "Distance: -")
        with c5:
            if use_toggle:
                new_flag = st.toggle(
                    "Ready to share",
                    value=current_flag,
                    key=f"share_{eid}",
                    help="Mark this equipment as available to share with other clients."
                )
            else:
                new_flag = st.checkbox(
                    "Ready to share",
                    value=current_flag,
                    key=f"share_{eid}",
                    help="Mark this equipment as available to share with other clients."
                )

            if new_flag != current_flag:
                try:
                    mark_ready_to_share(eid, new_flag, current_site_id if new_flag else None)
                    st.success(f"{eid} marked {'ready' if new_flag else 'not ready'} to share.")
                    # Force refresh so table state reflects the update immediately
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Failed to update share flag for {eid}: {e}")
