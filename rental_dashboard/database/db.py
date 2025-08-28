import sqlite3
from utils.config import DB_PATH
from datetime import datetime, timedelta

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Vendor/Equipment Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Vendor (
        EquipmentID TEXT PRIMARY KEY,
        Type TEXT,
        SiteID INTEGER,
        CheckOutDate TEXT,
        CheckInDate TEXT,
        EngineHourDay REAL,
        IdleHourDay REAL,
        OperatingDays INTEGER,
        DaysLeft INTEGER,
        Fuel REAL,
        Location TEXT,
        Availability TEXT CHECK(Availability IN ('Available', 'Rented')) DEFAULT 'Available',
        RentalType TEXT
    )
    """)

    # Site Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SiteInfo (
        SiteID INTEGER,
        EquipmentID TEXT,
        Location TEXT,
        ContactDetails TEXT,
        FOREIGN KEY (EquipmentID) REFERENCES Vendor(EquipmentID)
    )
    """)

    # 🔹 Pre-populate Vendor table if empty
    cursor.execute("SELECT COUNT(*) FROM Vendor")
    count = cursor.fetchone()[0]

    if count == 0:
        equipment_list = [
        # 25 Excavators
        ('EQX1001', 'Excavator', 'Available'),
        ('EQX1002', 'Excavator', 'Available'),
        ('EQX1003', 'Excavator', 'Available'),
        ('EQX1004', 'Excavator', 'Available'),
        ('EQX1005', 'Excavator', 'Available'),
        ('EQX1006', 'Excavator', 'Available'),
        ('EQX1007', 'Excavator', 'Available'),
        ('EQX1008', 'Excavator', 'Available'),
        ('EQX1009', 'Excavator', 'Available'),
        ('EQX1010', 'Excavator', 'Available'),
        ('EQX1011', 'Excavator', 'Available'),
        ('EQX1012', 'Excavator', 'Available'),
        ('EQX1013', 'Excavator', 'Available'),
        ('EQX1014', 'Excavator', 'Available'),
        ('EQX1015', 'Excavator', 'Available'),
        ('EQX1016', 'Excavator', 'Available'),
        ('EQX1017', 'Excavator', 'Available'),
        ('EQX1018', 'Excavator', 'Available'),
        ('EQX1019', 'Excavator', 'Available'),
        ('EQX1020', 'Excavator', 'Available'),
        ('EQX1021', 'Excavator', 'Available'),
        ('EQX1022', 'Excavator', 'Available'),
        ('EQX1023', 'Excavator', 'Available'),
        ('EQX1024', 'Excavator', 'Available'),
        ('EQX1025', 'Excavator', 'Available'),

        # 25 Cranes
        ('EQX1026', 'Crane', 'Available'),
        ('EQX1027', 'Crane', 'Available'),
        ('EQX1028', 'Crane', 'Available'),
        ('EQX1029', 'Crane', 'Available'),
        ('EQX1030', 'Crane', 'Available'),
        ('EQX1031', 'Crane', 'Available'),
        ('EQX1032', 'Crane', 'Available'),
        ('EQX1033', 'Crane', 'Available'),
        ('EQX1034', 'Crane', 'Available'),
        ('EQX1035', 'Crane', 'Available'),
        ('EQX1036', 'Crane', 'Available'),
        ('EQX1037', 'Crane', 'Available'),
        ('EQX1038', 'Crane', 'Available'),
        ('EQX1039', 'Crane', 'Available'),
        ('EQX1040', 'Crane', 'Available'),
        ('EQX1041', 'Crane', 'Available'),
        ('EQX1042', 'Crane', 'Available'),
        ('EQX1043', 'Crane', 'Available'),
        ('EQX1044', 'Crane', 'Available'),
        ('EQX1045', 'Crane', 'Available'),
        ('EQX1046', 'Crane', 'Available'),
        ('EQX1047', 'Crane', 'Available'),
        ('EQX1048', 'Crane', 'Available'),
        ('EQX1049', 'Crane', 'Available'),
        ('EQX1050', 'Crane', 'Available'),

        # 25 Bulldozers
        ('EQX1051', 'Bulldozer', 'Available'),
        ('EQX1052', 'Bulldozer', 'Available'),
        ('EQX1053', 'Bulldozer', 'Available'),
        ('EQX1054', 'Bulldozer', 'Available'),
        ('EQX1055', 'Bulldozer', 'Available'),
        ('EQX1056', 'Bulldozer', 'Available'),
        ('EQX1057', 'Bulldozer', 'Available'),
        ('EQX1058', 'Bulldozer', 'Available'),
        ('EQX1059', 'Bulldozer', 'Available'),
        ('EQX1060', 'Bulldozer', 'Available'),
        ('EQX1061', 'Bulldozer', 'Available'),
        ('EQX1062', 'Bulldozer', 'Available'),
        ('EQX1063', 'Bulldozer', 'Available'),
        ('EQX1064', 'Bulldozer', 'Available'),
        ('EQX1065', 'Bulldozer', 'Available'),
        ('EQX1066', 'Bulldozer', 'Available'),
        ('EQX1067', 'Bulldozer', 'Available'),
        ('EQX1068', 'Bulldozer', 'Available'),
        ('EQX1069', 'Bulldozer', 'Available'),
        ('EQX1070', 'Bulldozer', 'Available'),
        ('EQX1071', 'Bulldozer', 'Available'),
        ('EQX1072', 'Bulldozer', 'Available'),
        ('EQX1073', 'Bulldozer', 'Available'),
        ('EQX1074', 'Bulldozer', 'Available'),
        ('EQX1075', 'Bulldozer', 'Available'),

        # 25 Graders
        ('EQX1076', 'Grader', 'Available'),
        ('EQX1077', 'Grader', 'Available'),
        ('EQX1078', 'Grader', 'Available'),
        ('EQX1079', 'Grader', 'Available'),
        ('EQX1080', 'Grader', 'Available'),
        ('EQX1081', 'Grader', 'Available'),
        ('EQX1082', 'Grader', 'Available'),
        ('EQX1083', 'Grader', 'Available'),
        ('EQX1084', 'Grader', 'Available'),
        ('EQX1085', 'Grader', 'Available'),
        ('EQX1086', 'Grader', 'Available'),
        ('EQX1087', 'Grader', 'Available'),
        ('EQX1088', 'Grader', 'Available'),
        ('EQX1089', 'Grader', 'Available'),
        ('EQX1090', 'Grader', 'Available'),
        ('EQX1091', 'Grader', 'Available'),
        ('EQX1092', 'Grader', 'Available'),
        ('EQX1093', 'Grader', 'Available'),
        ('EQX1094', 'Grader', 'Available'),
        ('EQX1095', 'Grader', 'Available'),
        ('EQX1096', 'Grader', 'Available'),
        ('EQX1097', 'Grader', 'Available'),
        ('EQX1098', 'Grader', 'Available'),
        ('EQX1099', 'Grader', 'Available'),
        ('EQX1100', 'Grader', 'Available')
        ]


        cursor.executemany("""
        INSERT INTO Vendor (EquipmentID, Type, Availability)
        VALUES (?, ?, ?)
        """, equipment_list)

        conn.commit()
        print("✅ Vendor table pre-populated with default equipment data.")

    conn.close()

# Insert Site
def insert_site(site_id, location, contact):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SiteInfo (SiteID, Location, ContactDetails) VALUES (?, ?, ?)",
                   (site_id, location, contact))
    conn.commit()
    conn.close()

# Insert Vendor/Equipment
def insert_vendor(type_, site_id, operating_days, location, start_date, rental_type, availability="Available"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Vendor (Type, SiteID, OperatingDays, Location, CheckOutDate, Availability, RentalType)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (type_, site_id, operating_days, location, start_date, availability, rental_type))
    conn.commit()
    conn.close()

# Fetch Vendors (with filters)
def fetch_vendors(filter_by=None, site_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM Vendor WHERE 1=1"
    params = []
    
    if filter_by == "Available":
        query += " AND Availability='Available'"
    elif filter_by == "Rented":
        query += " AND Availability='Rented'"
    
    if site_id:
        query += " AND SiteID=?"
        params.append(site_id)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_available_types():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT Type
        FROM Vendor
        WHERE Availability = 'Available'
    """)
    types = [row[0] for row in cursor.fetchall()]
    conn.close()
    return types

# Get one available equipmentID for a given type
def get_available_equipment(type_):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT EquipmentID FROM Vendor WHERE Type=? AND Availability='Available' LIMIT 1", (type_,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Update Vendor row when rented
def rent_equipment(equipment_id, site_id, operating_days, location, start_date, rental_type):
    conn = get_connection()
    cursor = conn.cursor()

    # Compute end date and days left
    cursor.execute("SELECT date(?, '+' || ? || ' days')", (start_date, operating_days))
    end_date = cursor.fetchone()[0]

    cursor.execute("SELECT julianday(?) - julianday('now')", (end_date,))
    days_left = int(cursor.fetchone()[0])

    # Update Vendor table (mark rented + add details)
    cursor.execute("""
        UPDATE Vendor
        SET SiteID = ?,
            CheckOutDate = ?,
            CheckInDate = ?,
            OperatingDays = ?,
            DaysLeft = ?,
            Location = ?,
            RentalType = ?,
            Availability = 'Rented'
        WHERE EquipmentID = ?
    """, (site_id, start_date, end_date, operating_days, days_left, location, rental_type, equipment_id))

    conn.commit()
    conn.close()

def get_available_equipment_ids(type_):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EquipmentID
        FROM Vendor
        WHERE Type = ? AND Availability = 'Available'
    """, (type_,))
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

