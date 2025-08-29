# modules/map_view.py
import time
import pandas as pd
import streamlit as st
import pydeck as pdk

from database.db import get_connection
from database.locations import geocode_name, allowed_location_names


# --- DATA LAYER --------------------------------------------------------------

@st.cache_data(show_spinner=False, ttl=5)  # auto-expire cached data every 5s
def get_equipment_geodata():
    """
    Build dataframe with:
      EquipmentID, Type, SiteID, Availability, RentalType, ReadyToShare, Fuel,
      lat, lon, name_source ('Vendor'|'SiteInfoEq'|'SiteInfoSite'), loc_name.

    Strategy:
      1) Try Vendor.Location as a human-readable name.
      2) If unresolved, try SiteInfo.Location by EquipmentID.
      3) If still unresolved, try SiteInfo.Location by SiteID.
      4) Keep only rows that resolve to an allowed name (per geocode_name).
    """
    with get_connection() as conn:
        v = pd.read_sql_query(
            """
            SELECT EquipmentID, Type, SiteID, Location, Availability, RentalType, ReadyToShare, Fuel
            FROM Vendor
            """,
            conn,
        )
        s = pd.read_sql_query(
            "SELECT SiteID, EquipmentID, Location AS SiteLocation FROM SiteInfo",
            conn,
        )

    # Step 1: resolve from Vendor.Location
    def resolve_name(name):
        lat, lon, key = geocode_name(name)
        if lat is not None and lon is not None:
            return pd.Series({"lat": lat, "lon": lon, "loc_name": key})
        return pd.Series({"lat": None, "lon": None, "loc_name": None})

    first = v["Location"].apply(resolve_name)
    v = pd.concat([v, first], axis=1)
    v["name_source"] = v.apply(lambda r: "Vendor" if pd.notnull(r["lat"]) and pd.notnull(r["lon"]) else None, axis=1)

    # Step 2: unresolved -> try SiteInfo by EquipmentID
    if not s.empty:
        by_eq = s[["EquipmentID", "SiteLocation"]]
        v = v.merge(by_eq, on="EquipmentID", how="left")
        need = v["lat"].isna() | v["lon"].isna()
        if need.any():
            sf = v.loc[need, "SiteLocation"].apply(resolve_name)
            v.loc[need, ["lat", "lon", "loc_name"]] = sf[["lat", "lon", "loc_name"]].values
            v.loc[need & sf["lat"].notna(), "name_source"] = "SiteInfoEq"

    # Step 3: still unresolved -> try SiteInfo by SiteID
    if not s.empty:
        by_site = s.groupby("SiteID")["SiteLocation"].first().reset_index()
        v = v.merge(by_site, on="SiteID", how="left", suffixes=("", "_site"))
        need2 = v["lat"].isna() | v["lon"].isna()
        if need2.any():
            sf2 = v.loc[need2, "SiteLocation_site"].apply(resolve_name)
            v.loc[need2, ["lat", "lon", "loc_name"]] = sf2[["lat", "lon", "loc_name"]].values
            v.loc[need2 & sf2["lat"].notna(), "name_source"] = "SiteInfoSite"

    # Keep only resolved rows
    v = v[pd.notnull(v["lat"]) & pd.notnull(v["lon"])].copy()

    # Labels & flags
    def fuel_str(x):
        try:
            return f" | Fuel: {float(x):.0f}%"
        except Exception:
            return ""
    v["label"] = (
        "ID: " + v["EquipmentID"].astype(str)
        + " | " + v["Type"].astype(str)
        + " | " + v["Availability"].astype(str)
        + v["Fuel"].apply(fuel_str)
    )
    v["is_share"] = (v["ReadyToShare"].fillna(0).astype(int) == 1)
    v["is_rented"] = v["Availability"].str.upper().eq("RENTED")
    return v


# --- VIEW LAYER --------------------------------------------------------------

def equipment_map_view():
    st.title("Equipment Distribution Map (by Location Name)")

    # Controls first so a change triggers rerun
    with st.sidebar:
        st.subheader("Live updates")
        auto_refresh = st.checkbox("Auto-refresh", value=True, help="Re-run the page automatically.")
        refresh_every = st.number_input("Seconds", min_value=2, max_value=120, value=5, step=1)
        colr1, colr2 = st.columns([1,1])
        with colr1:
            if st.button("Refresh now"):
                st.cache_data.clear()   # clear cached frames immediately
                st.rerun()

        with colr2:
            if st.button("Clear cache"):
                st.cache_data.clear()

    # Fetch data (cached with small TTL)
    df = get_equipment_geodata()

    if df.empty:
        st.info(
            "No equipment resolved to an allowed location name. "
            "Update Vendor.Location or SiteInfo.Location to a supported name."
        )
        with st.expander("Allowed location names (canonical)"):
            st.write(", ".join(allowed_location_names()))
        # Auto-refresh loop even if empty (helpful right after inserting new rows)
        if auto_refresh:
            time.sleep(int(refresh_every))
            st.experimental_rerun()
        return

    # Sidebar filters
    with st.sidebar:
        st.subheader("Map Filters")
        type_opts = ["All"] + sorted(df["Type"].dropna().unique().tolist())
        chosen_type = st.selectbox("Type", type_opts, index=0)

        avail_opts = ["All", "Available", "Rented"]
        chosen_avail = st.selectbox("Availability", avail_opts, index=0)

        share_only = st.checkbox("Show only Ready To Share", value=False)

        st.markdown("---")
        view_mode = st.radio("Map mode", ["Intensity (by location)", "Pins (per unit)", "Heatmap"], index=0)
        base_radius_m = st.slider("Intensity bubble base size (meters)", 3000, 20000, 7000, 100)

    # Apply filters
    filtered = df.copy()
    if chosen_type != "All":
        filtered = filtered[filtered["Type"] == chosen_type]
    if chosen_avail != "All":
        filtered = filtered[filtered["Availability"].str.capitalize() == chosen_avail]
    if share_only:
        filtered = filtered[filtered["is_share"]]

    if filtered.empty:
        st.warning("No equipment matches your filters.")
        if auto_refresh:
            time.sleep(int(refresh_every))
            st.experimental_rerun()
        return

    # Center map
    center_lat = float(filtered["lat"].mean())
    center_lon = float(filtered["lon"].mean())
    pitch = 20 if view_mode != "Pins (per unit)" else 0
    zoom = 5 if view_mode != "Pins (per unit)" else 4
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom, pitch=pitch)

    layers = []
    tooltip = None

    if view_mode == "Pins (per unit)":
        # Color by status
        def color_row(r):
            if r["is_share"]:
                return [0, 200, 80, 200]   # ReadyToShare
            if r["is_rented"]:
                return [220, 60, 60, 200]  # Rented
            return [60, 100, 240, 200]     # Available

        dfpins = filtered.copy()
        dfpins["color"] = dfpins.apply(color_row, axis=1)

        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=dfpins,
                get_position='[lon, lat]',
                get_radius=8000,
                get_fill_color="color",
                pickable=True,
                radius_min_pixels=4,
                radius_max_pixels=24,
            )
        )

        tooltip = {
            "html": (
                "<b>{EquipmentID}</b><br/>"
                "Type: {Type}<br/>"
                "Site: {SiteID}<br/>"
                "Availability: {Availability}<br/>"
                "RentalType: {RentalType}<br/>"
                "ReadyToShare: {ReadyToShare}<br/>"
                "At: {loc_name}"
            ),
            "style": {"backgroundColor": "rgba(30,30,30,0.9)", "color": "white"},
        }

    elif view_mode == "Intensity (by location)":
        # Aggregate by location
        agg = (
            filtered.groupby(["loc_name", "lat", "lon"], as_index=False)
            .agg(
                count=("EquipmentID", "size"),
                rented=("is_rented", "sum"),
                share=("is_share", "sum"),
            )
        )

        # Radius scales with sqrt(count)
        agg["radius_m"] = (agg["count"] ** 0.5) * float(base_radius_m)

        # Color by mix
        def color_by_mix(row):
            if row["count"] == 0:
                return [150, 150, 150, 200]
            share_ratio = row["share"] / row["count"]
            rent_ratio = row["rented"] / row["count"]
            if share_ratio >= 0.5:
                return [0, 200, 80, 220]     # mostly ReadyToShare
            if rent_ratio >= 0.5:
                return [220, 60, 60, 220]    # mostly Rented
            return [60, 100, 240, 220]       # mostly Available or mixed

        agg["color"] = agg.apply(color_by_mix, axis=1)

        # Scaled bubbles
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=agg,
                get_position='[lon, lat]',
                get_radius="radius_m",
                get_fill_color="color",
                pickable=True,
                stroked=True,
                get_line_color=[255, 255, 255, 100],
                line_width_min_pixels=1,
            )
        )

        # Labels showing counts
        layers.append(
            pdk.Layer(
                "TextLayer",
                data=agg,
                get_position='[lon, lat]',
                get_text='count',
                get_size=14,
                get_color=[0, 0, 0, 255],
                get_angle=0,
                get_alignment_baseline="'top'",
            )
        )

        tooltip = {
            "html": (
                "<b>{loc_name}</b><br/>"
                "Total: {count}<br/>"
                "Rented: {rented} | ReadyToShare: {share}"
            ),
            "style": {"backgroundColor": "rgba(30,30,30,0.9)", "color": "white"},
        }

    else:  # Heatmap
        layers.append(
            pdk.Layer(
                "HeatmapLayer",
                data=filtered,
                get_position='[lon, lat]',
                get_weight=1,
                radiusPixels=60,
                intensity=1,
                threshold=0.01,
            )
        )
        # Optional overlay: counts per location
        agg = (
            filtered.groupby(["loc_name", "lat", "lon"], as_index=False)
            .agg(count=("EquipmentID", "size"))
        )
        layers.append(
            pdk.Layer(
                "TextLayer",
                data=agg,
                get_position='[lon, lat]',
                get_text='count',
                get_size=12,
                get_color=[0, 0, 0, 255],
                get_angle=0,
                get_alignment_baseline="'top'",
            )
        )
        tooltip = None  # HeatmapLayer doesn't do per-point tooltips

    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state, tooltip=tooltip))

    # Debug unresolved
    with st.expander("Unresolved equipment (debug)"):
        with get_connection() as conn:
            raw = pd.read_sql_query("SELECT EquipmentID, SiteID, Location FROM Vendor", conn)
            unresolved = raw[~raw["EquipmentID"].isin(df["EquipmentID"])]
        if unresolved.empty:
            st.caption("All items resolved to allowed locations.")
        else:
            st.dataframe(unresolved, use_container_width=True)

    # Legend
    st.markdown(
        """
**Legend**
- 🟢 Mostly Ready to Share  
- 🔴 Mostly Rented  
- 🔵 Mostly Available/Mixed  

**Modes**
- **Intensity (by location):** bubble size ∝ √(equipment count). Label shows count.
- **Pins (per unit):** one dot per equipment, color = status.
- **Heatmap:** density shading.

**Live updates**
- Auto-refresh re-runs this page every N seconds and the cached data expires every 5s.
- Use **Refresh now** if you just inserted a row and want an immediate update.
        """
    )

    # Auto-refresh at the very end so the page renders before sleeping
    if auto_refresh:
        time.sleep(int(refresh_every))
        st.rerun()

