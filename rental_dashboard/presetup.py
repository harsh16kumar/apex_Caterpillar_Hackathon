import sqlite3
from utils.config import DB_PATH

equipment_data = [
    ('EQX1001', 'Excavator', True),
    ('EQX1002', 'Crane', True),
    ('EQX1003', 'Bulldozer', True),
    ('EQX1004', 'Grader', True),
    ('EQX1005', 'Excavator', True),
    ('EQX1006', 'Crane', True),
    ('EQX1007', 'Bulldozer', True),
    ('EQX1008', 'Grader', True),
    ('EQX1009', 'Excavator', True),
    ('EQX1010', 'Crane', True),
    ('EQX1011', 'Bulldozer', True),
    ('EQX1012', 'Grader', True),
    ('EQX1013', 'Excavator', True),
    ('EQX1014', 'Crane', True),
    ('EQX1015', 'Bulldozer', True),
    ('EQX1016', 'Grader', True),
    ('EQX1017', 'Excavator', True),
    ('EQX1018', 'Crane', True),
    ('EQX1019', 'Bulldozer', True),
    ('EQX1020', 'Grader', True)
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Equipment (
        EquipmentID TEXT PRIMARY KEY,
        Type TEXT NOT NULL,
        Availability BOOLEAN NOT NULL
    )
''')

cursor.executemany('''
    INSERT INTO Equipment (EquipmentID, Type, Availability)
    VALUES (?, ?, ?)
''', equipment_data)

conn.commit()
conn.close()

print("✅ Equipment data inserted successfully!")
