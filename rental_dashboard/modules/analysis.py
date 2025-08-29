# modules/analysis.py
import streamlit as st
import pandas as pd
import altair as alt
from prophet import Prophet
from sklearn.ensemble import IsolationForest
from streamlit_autorefresh import st_autorefresh
import numpy as np
import random
from datetime import datetime, timedelta


def generate_sample_data(n=200):
    """Generate synthetic rental data for testing analysis features."""
    np.random.seed(42)
    random.seed(42)

    # Removed "Dump Truck"
    equipment_types = ["Excavator", "Bulldozer", "Crane", "Loader"]
    site_ids = [1, 2, 3]

    data = []
    start_date = datetime.today() - timedelta(days=120)  # 4 months history

    for i in range(n):
        equipment_id = f"EQUIP_{1000+i}"
        equip_type = random.choice(equipment_types)
        site_id = random.choice(site_ids)

        # Rentals spread over ~120 days
        checkout_date = start_date + timedelta(days=random.randint(0, 110))
        checkin_date = checkout_date + timedelta(days=random.randint(1, 15))

        # Engine hours 4–12 hrs/day, idle hours 0–6 hrs/day
        engine_hours = np.round(np.random.uniform(4, 12), 1)
        idle_hours = np.round(np.random.uniform(0, 6), 1)

        # Inject anomalies (very high idle hours ~15% of the time)
        if random.random() < 0.15:
            idle_hours = np.round(np.random.uniform(12, 20), 1)

        operating_days = (checkin_date - checkout_date).days

        data.append([
            equipment_id,
            equip_type,
            site_id,
            checkout_date,
            checkin_date,
            engine_hours,
            idle_hours,
            operating_days
        ])

    df = pd.DataFrame(data, columns=[
        "EquipmentID", "Type", "SiteID", "CheckOutDate", "CheckInDate",
        "EngineHourDay", "IdleHourDay", "OperatingDays"
    ])
    return df


def demand_forecast_view():
    st.header("📊 Real-Time Equipment Demand Forecast, Anomalies & Utilization")

    # 🔄 Auto refresh every 15 seconds
    st_autorefresh(interval=15 * 1000, key="data_refresh")

    # Load synthetic data
    df = generate_sample_data(200)

    # --- Site selection ---
    site_list = df['SiteID'].dropna().unique()
    site_id = st.selectbox("Select Site", site_list)

    # --- Demand Forecast ---
    st.subheader("🔮 Demand Forecast (Next 30 Days)")
    site_df = df[df['SiteID'] == site_id].copy()

    # Rentals per day (historical demand)
    daily_rentals = site_df.groupby('CheckOutDate').size().reset_index(name='Rentals')
    daily_rentals.rename(columns={'CheckOutDate': 'ds', 'Rentals': 'y'}, inplace=True)

    if daily_rentals.shape[0] < 2:
        st.info("ℹ Not enough rental history for forecasting.")
    else:
        model = Prophet(daily_seasonality=True)
        model.fit(daily_rentals)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(
            columns={
                'ds': 'Date',
                'yhat': 'Predicted Rentals',
                'yhat_lower': 'Lower Estimate',
                'yhat_upper': 'Upper Estimate'
            }
        )
        forecast_display['Predicted Rentals'] = forecast_display['Predicted Rentals'].round().astype(int)

        st.line_chart(forecast_display.set_index('Date')['Predicted Rentals'])
        st.dataframe(forecast_display.tail(10))

    # --- Anomaly Detection ---
    st.subheader("⚠ Real-Time Anomaly Detection (based on unusual Idle vs Engine hours)")
    try:
        iso = IsolationForest(contamination=0.1, random_state=42)
        df['IdleAnomaly'] = iso.fit_predict(df[['EngineHourDay', 'IdleHourDay']])
        anomalies = df[df['IdleAnomaly'] == -1]

        st.metric("Anomalies Detected", len(anomalies))
        st.dataframe(
            anomalies[['EquipmentID', 'SiteID', 'EngineHourDay',
                       'IdleHourDay', 'CheckOutDate', 'CheckInDate']]
        )

        st.altair_chart(
            alt.Chart(df)
            .mark_circle(size=60)
            .encode(
                x='EngineHourDay',
                y='IdleHourDay',
                color=alt.condition(
                    alt.datum.IdleAnomaly == -1, alt.value('red'), alt.value('blue')
                ),
                tooltip=['EquipmentID', 'Type', 'SiteID', 'EngineHourDay', 'IdleHourDay']
            )
            .interactive(),
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Anomaly detection failed: {e}")

    # --- Underutilization Detection ---
    st.subheader("🛠 Underutilized Equipment (High Idle Ratio)")
    df['UtilizationRatio'] = df['EngineHourDay'] / (df['EngineHourDay'] + df['IdleHourDay'])
    underutilized = df[df['UtilizationRatio'] < 0.4]  # threshold: <40% productive use

    st.metric("Underutilized Equipment Count", len(underutilized))
    st.dataframe(
        underutilized[['EquipmentID', 'Type', 'SiteID', 'EngineHourDay',
                       'IdleHourDay', 'UtilizationRatio']]
    )