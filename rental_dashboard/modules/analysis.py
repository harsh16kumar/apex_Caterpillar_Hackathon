# modules/analysis.py
import streamlit as st
import pandas as pd
import altair as alt
from prophet import Prophet
from sklearn.ensemble import IsolationForest
from database.db import fetch_vendors
from streamlit_autorefresh import st_autorefresh


def demand_forecast_view():
    st.header("📊 Real-Time Equipment Demand Forecast, Anomalies & Utilization")

    # 🔄 Auto refresh every 15 seconds
    st_autorefresh(interval=15 * 1000, key="data_refresh")

    # Load latest vendor data
    data = fetch_vendors()
    if not data:
        st.warning("⚠️ No vendor data available yet.")
        return

    # ✅ Convert to DataFrame and keep first 8 columns
    df = pd.DataFrame(data)
    df = df.iloc[:, :8]
    df.columns = [
        "EquipmentID", "Type", "SiteID", "CheckOutDate",
        "CheckInDate", "EngineHourDay", "IdleHourDay", "OperatingDays"
    ]

    # --- Site selection ---
    site_list = df['SiteID'].dropna().unique()
    if len(site_list) == 0:
        st.warning("⚠️ No sites found in data.")
        return

    site_id = st.selectbox("Select Site", site_list)

    # --- Demand Forecast ---
    st.subheader("🔮 Demand Forecast (Next 30 Days)")
    site_df = df[df['SiteID'] == site_id].copy()

    # Count rentals per day
    daily_rentals = site_df.groupby('CheckOutDate').size().reset_index(name='Rentals')
    daily_rentals.rename(columns={'CheckOutDate': 'ds', 'Rentals': 'y'}, inplace=True)

    if daily_rentals.shape[0] < 2:
        st.info("ℹ️ Not enough rental history for forecasting.")
    else:
        model = Prophet(daily_seasonality=True)
        model.fit(daily_rentals)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        # Round predicted rentals
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
    st.subheader("⚠️ Real-Time Anomaly Detection (Idle vs Engine Hours)")
    st.caption("Anomalies are flagged when equipment shows unusual idle-to-engine hour ratios using Isolation Forest.")

    if "IdleHourDay" in df and "EngineHourDay" in df:
        try:
            iso = IsolationForest(contamination=0.05, random_state=42)
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
    else:
        st.info("Idle/Engine hour data not available for anomaly detection.")

    # --- Underutilized Equipment ---
    st.subheader("🟡 Underutilized Equipment Analysis")

    if "OperatingDays" in df and "IdleHourDay" in df and "EngineHourDay" in df:
        try:
            utilization = df.copy()
            utilization['UtilizationRatio'] = utilization['EngineHourDay'] / (
                utilization['EngineHourDay'] + utilization['IdleHourDay'] + 1e-6
            )

            # Threshold: less than 30% engine usage = underutilized
            underutilized = utilization[utilization['UtilizationRatio'] < 0.3]

            if underutilized.empty:
                st.success("✅ No significantly underutilized equipment detected.")
            else:
                st.warning(f"⚠️ {len(underutilized)} underutilized equipment detected.")
                st.dataframe(
                    underutilized[['EquipmentID', 'Type', 'SiteID',
                                   'EngineHourDay', 'IdleHourDay', 'OperatingDays', 'UtilizationRatio']]
                )

                st.altair_chart(
                    alt.Chart(utilization)
                    .mark_bar()
                    .encode(
                        x='EquipmentID:N',
                        y='UtilizationRatio:Q',
                        color=alt.condition(
                            alt.datum.UtilizationRatio < 0.3, alt.value('orange'), alt.value('green')
                        ),
                        tooltip=['EquipmentID', 'Type', 'SiteID',
                                 'EngineHourDay', 'IdleHourDay', 'UtilizationRatio']
                    )
                    .properties(height=400)
                    .interactive(),
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Underutilization analysis failed: {e}")
    else:
        st.info("Operating/Idle/Engine hour data not sufficient for utilization analysis.")
