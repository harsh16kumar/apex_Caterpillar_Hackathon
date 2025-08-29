import pandas as pd
from database.db import get_connection
from utils.notifications import send_email_node   # assuming you move your email code here

def check_and_notify_low_utilization(threshold: float = 5.0):
    """
    Calculates average EngineHourDay + IdleHourDay grouped by (SiteID, Type).
    If below threshold, sends email to SiteInfo contacts.
    """

    with get_connection() as conn:
        # Join Vendor with SiteInfo to fetch contacts
        q = """
        SELECT 
            v.SiteID,
            v.Type,
            COALESCE(v.EngineHourDay, 0) AS EngineHourDay,
            COALESCE(v.IdleHourDay, 0) AS IdleHourDay,
            s.ContactDetails
        FROM Vendor v
        LEFT JOIN SiteInfo s ON v.SiteID = s.SiteID
        """
        df = pd.read_sql_query(q, conn)

    if df.empty:
        print("⚠️ No equipment data found.")
        return
    
    grouped = (
        df.groupby(["SiteID", "Type", "ContactDetails"])
        .agg(avg_usage=pd.NamedAgg(column="EngineHourDay", aggfunc="mean"))
        .reset_index()
    )

    grouped["avg_usage"] += (
        df.groupby(["SiteID", "Type", "ContactDetails"])["IdleHourDay"].mean().values
    )

    for _, row in grouped.iterrows():
        site_id = row["SiteID"]
        type_ = row["Type"]
        avg_usage = row["avg_usage"]
        contact_email = row["ContactDetails"]

        if avg_usage < threshold and contact_email:
            print(f"⚠️ Site {site_id} ({type_}) low usage detected: {avg_usage:.2f} hrs/day")
            
            state = {
                "email_id": contact_email,
                "subject": f"Low Utilization Alert - Site {site_id}",
                "message": (
                    f"Equipment type {type_} at Site {site_id} "
                    f"is averaging only {avg_usage:.2f} hrs/day, below the threshold of {threshold}."
                ),
            }
            send_email_node(state)
        else:
            print(f"✅ Site {site_id}, Type {type_} has sufficient utilization ({avg_usage:.2f})")

    return grouped
