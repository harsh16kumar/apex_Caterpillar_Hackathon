# database/geo.py
import sqlite3
from utils.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def ensure_geo_columns():
    """
    Ensure SiteInfo has Latitude/Longitude, and Vendor has GeoLocation (optional).
    Won't drop or overwrite anything.
    """
    with get_connection() as conn:
        cur = conn.cursor()

        # Add columns to SiteInfo if missing
        cur.execute("PRAGMA table_info(SiteInfo)")
        site_cols = {r[1] for r in cur.fetchall()}

        if "Latitude" not in site_cols:
            cur.execute("ALTER TABLE SiteInfo ADD COLUMN Latitude REAL")
        if "Longitude" not in site_cols:
            cur.execute("ALTER TABLE SiteInfo ADD COLUMN Longitude REAL")

        # Optional: keep Vendor.Location as-is (string). If you prefer, also add numeric columns for Vendor.
        # cur.execute("PRAGMA table_info(Vendor)")
        # vendor_cols = {r[1] for r in cur.fetchall()}
        # if "Lat" not in vendor_cols:
        #     cur.execute("ALTER TABLE Vendor ADD COLUMN Lat REAL")
        # if "Lon" not in vendor_cols:
        #     cur.execute("ALTER TABLE Vendor ADD COLUMN Lon REAL")

        conn.commit()
