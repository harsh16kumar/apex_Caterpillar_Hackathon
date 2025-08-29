import sqlite3
from utils.config import DB_PATH
from datetime import datetime, timedelta
import pandas as pd

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def backfill_demo_site_ids():
    with get_connection() as conn:
        conn.execute("""
            UPDATE Vendor
            SET SiteID = CASE
                WHEN (CAST(substr(EquipmentID, 4) AS INTEGER) % 2) = 0 THEN 2
                ELSE 1
            END
            WHERE SiteID IS NULL
        """)
        conn.commit()

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
        RentalType TEXT CHECK(RentalType IN ('Rigid', 'Flexible')),
        ReadyToShare INTEGER DEFAULT 0,
        SharedBySiteID INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SiteInfo (
        SiteID INTEGER,
        EquipmentID TEXT,
        Location TEXT,
        ContactDetails TEXT,
        FOREIGN KEY (EquipmentID) REFERENCES Vendor(EquipmentID)
    )
    """)

    conn.execute("""
            CREATE TABLE IF NOT EXISTS RentalRequests (
                RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
                EquipmentID TEXT,
                RequesterSiteID INTEGER,
                OwnerSiteID INTEGER,
                Location TEXT,
                TimeFrom TEXT,
                TimeTo   TEXT,
                Status TEXT CHECK(Status IN ('Pending','Approved','Rejected')) DEFAULT 'Pending'
            )
    """)
    # If table existed before without OwnerSiteID, add it:
    # cur = conn.execute("PRAGMA table_info(RentalRequests)")
    # cols = {r[1] for r in cur.fetchall()}
    # if "OwnerSiteID" not in cols:
    #     conn.execute("ALTER TABLE RentalRequests ADD COLUMN OwnerSiteID INTEGER")
    # conn.commit()

    cursor.execute("SELECT COUNT(*) FROM Vendor")
    count = cursor.fetchone()[0]

    if count == 0:
        equipment_list = [
            
            ('EQX1151', 'Excavator', 'Available'),
            ('EQX1152', 'Excavator', 'Available'),
            ('EQX1153', 'Excavator', 'Available'),
            ('EQX1154', 'Excavator', 'Available'),
            ('EQX1155', 'Excavator', 'Available'),
            ('EQX1156', 'Excavator', 'Available'),
            ('EQX1157', 'Excavator', 'Available'),
            ('EQX1158', 'Excavator', 'Available'),
            ('EQX1159', 'Excavator', 'Available'),
            ('EQX1160', 'Excavator', 'Available'),
            ('EQX1161', 'Excavator', 'Available'),
            ('EQX1162', 'Excavator', 'Available'),
            ('EQX1163', 'Excavator', 'Available'),
            ('EQX1164', 'Excavator', 'Available'),
            ('EQX1165', 'Excavator', 'Available'),
            ('EQX1166', 'Excavator', 'Available'),
            ('EQX1167', 'Excavator', 'Available'),
            ('EQX1168', 'Excavator', 'Available'),
            ('EQX1169', 'Excavator', 'Available'),
            ('EQX1170', 'Excavator', 'Available'),
            ('EQX1171', 'Excavator', 'Available'),
            ('EQX1172', 'Excavator', 'Available'),
            ('EQX1173', 'Excavator', 'Available'),
            ('EQX1174', 'Excavator', 'Available'),
            ('EQX1175', 'Excavator', 'Available'),
            ('EQX1176', 'Excavator', 'Available'),
            ('EQX1177', 'Excavator', 'Available'),
            ('EQX1178', 'Excavator', 'Available'),
            ('EQX1179', 'Excavator', 'Available'),
            ('EQX1180', 'Excavator', 'Available'),
            ('EQX1181', 'Excavator', 'Available'),
            ('EQX1182', 'Excavator', 'Available'),
            ('EQX1183', 'Excavator', 'Available'),
            ('EQX1184', 'Excavator', 'Available'),
            ('EQX1185', 'Excavator', 'Available'),
            ('EQX1186', 'Excavator', 'Available'),
            ('EQX1187', 'Excavator', 'Available'),
            ('EQX1188', 'Excavator', 'Available'),
            ('EQX1189', 'Excavator', 'Available'),
            ('EQX1190', 'Excavator', 'Available'),
            ('EQX1191', 'Excavator', 'Available'),
            ('EQX1192', 'Excavator', 'Available'),
            ('EQX1193', 'Excavator', 'Available'),
            ('EQX1194', 'Excavator', 'Available'),
            ('EQX1195', 'Excavator', 'Available'),
            ('EQX1196', 'Excavator', 'Available'),
            ('EQX1197', 'Excavator', 'Available'),
            ('EQX1198', 'Excavator', 'Available'),
            ('EQX1199', 'Excavator', 'Available'),
            ('EQX1200', 'Excavator', 'Available'),
            ('EQX1201', 'Excavator', 'Available'),
            ('EQX1202', 'Excavator', 'Available'),
            ('EQX1203', 'Excavator', 'Available'),
            ('EQX1204', 'Excavator', 'Available'),
            ('EQX1205', 'Excavator', 'Available'),
            ('EQX1206', 'Excavator', 'Available'),
            ('EQX1207', 'Excavator', 'Available'),
            ('EQX1208', 'Excavator', 'Available'),
            ('EQX1209', 'Excavator', 'Available'),
            ('EQX1210', 'Excavator', 'Available'),
            ('EQX1211', 'Excavator', 'Available'),
            ('EQX1212', 'Excavator', 'Available'),
            ('EQX1213', 'Excavator', 'Available'),
            ('EQX1214', 'Excavator', 'Available'),
            ('EQX1215', 'Excavator', 'Available'),
            ('EQX1216', 'Excavator', 'Available'),
            ('EQX1217', 'Excavator', 'Available'),
            ('EQX1218', 'Excavator', 'Available'),
            ('EQX1219', 'Excavator', 'Available'),
            ('EQX1220', 'Excavator', 'Available'),
            ('EQX1221', 'Excavator', 'Available'),
            ('EQX1222', 'Excavator', 'Available'),
            ('EQX1223', 'Excavator', 'Available'),
            ('EQX1224', 'Excavator', 'Available'),
            ('EQX1225', 'Excavator', 'Available'),
            ('EQX1226', 'Excavator', 'Available'),
            ('EQX1227', 'Excavator', 'Available'),
            ('EQX1228', 'Excavator', 'Available'),
            ('EQX1229', 'Excavator', 'Available'),
            ('EQX1230', 'Excavator', 'Available'),
            ('EQX1231', 'Excavator', 'Available'),
            ('EQX1232', 'Excavator', 'Available'),
            ('EQX1233', 'Excavator', 'Available'),
            ('EQX1234', 'Excavator', 'Available'),
            ('EQX1235', 'Excavator', 'Available'),
            ('EQX1236', 'Excavator', 'Available'),
            ('EQX1237', 'Excavator', 'Available'),
            ('EQX1238', 'Excavator', 'Available'),
            ('EQX1239', 'Excavator', 'Available'),
            ('EQX1240', 'Excavator', 'Available'),
            ('EQX1241', 'Excavator', 'Available'),
            ('EQX1242', 'Excavator', 'Available'),
            ('EQX1243', 'Excavator', 'Available'),
            ('EQX1244', 'Excavator', 'Available'),
            ('EQX1245', 'Excavator', 'Available'),
            ('EQX1246', 'Excavator', 'Available'),
            ('EQX1247', 'Excavator', 'Available'),
            ('EQX1248', 'Excavator', 'Available'),
            ('EQX1249', 'Excavator', 'Available'),
            ('EQX1250', 'Excavator', 'Available'),
            ('EQX1400', 'Crane', 'Available'),
            ('EQX1401', 'Crane', 'Available'),
            ('EQX1402', 'Crane', 'Available'),
            ('EQX1403', 'Crane', 'Available'),
            ('EQX1404', 'Crane', 'Available'),
            ('EQX1405', 'Crane', 'Available'),
            ('EQX1406', 'Crane', 'Available'),
            ('EQX1407', 'Crane', 'Available'),
            ('EQX1408', 'Crane', 'Available'),
            ('EQX1409', 'Crane', 'Available'),
            ('EQX1410', 'Crane', 'Available'),
            ('EQX1411', 'Crane', 'Available'),
            ('EQX1412', 'Crane', 'Available'),
            ('EQX1413', 'Crane', 'Available'),
            ('EQX1414', 'Crane', 'Available'),
            ('EQX1415', 'Crane', 'Available'),
            ('EQX1416', 'Crane', 'Available'),
            ('EQX1417', 'Crane', 'Available'),
            ('EQX1418', 'Crane', 'Available'),
            ('EQX1419', 'Crane', 'Available'),
            ('EQX1420', 'Crane', 'Available'),
            ('EQX1421', 'Crane', 'Available'),
            ('EQX1422', 'Crane', 'Available'),
            ('EQX1423', 'Crane', 'Available'),
            ('EQX1424', 'Crane', 'Available'),
            ('EQX1425', 'Crane', 'Available'),
            ('EQX1426', 'Crane', 'Available'),
            ('EQX1427', 'Crane', 'Available'),
            ('EQX1428', 'Crane', 'Available'),
            ('EQX1429', 'Crane', 'Available'),
            ('EQX1430', 'Crane', 'Available'),
            ('EQX1431', 'Crane', 'Available'),
            ('EQX1432', 'Crane', 'Available'),
            ('EQX1433', 'Crane', 'Available'),
            ('EQX1434', 'Crane', 'Available'),
            ('EQX1435', 'Crane', 'Available'),
            ('EQX1436', 'Crane', 'Available'),
            ('EQX1437', 'Crane', 'Available'),
            ('EQX1438', 'Crane', 'Available'),
            ('EQX1439', 'Crane', 'Available'),
            ('EQX1440', 'Crane', 'Available'),
            ('EQX1441', 'Crane', 'Available'),
            ('EQX1442', 'Crane', 'Available'),
            ('EQX1443', 'Crane', 'Available'),
            ('EQX1444', 'Crane', 'Available'),
            ('EQX1445', 'Crane', 'Available'),
            ('EQX1446', 'Crane', 'Available'),
            ('EQX1447', 'Crane', 'Available'),
            ('EQX1448', 'Crane', 'Available'),
            ('EQX1449', 'Crane', 'Available'),
            ('EQX1450', 'Crane', 'Available'),
            ('EQX1451', 'Crane', 'Available'),
            ('EQX1452', 'Crane', 'Available'),
            ('EQX1453', 'Crane', 'Available'),
            ('EQX1454', 'Crane', 'Available'),
            ('EQX1455', 'Crane', 'Available'),
            ('EQX1456', 'Crane', 'Available'),
            ('EQX1457', 'Crane', 'Available'),
            ('EQX1458', 'Crane', 'Available'),
            ('EQX1459', 'Crane', 'Available'),
            ('EQX1460', 'Crane', 'Available'),
            ('EQX1461', 'Crane', 'Available'),
            ('EQX1462', 'Crane', 'Available'),
            ('EQX1463', 'Crane', 'Available'),
            ('EQX1464', 'Crane', 'Available'),
            ('EQX1465', 'Crane', 'Available'),
            ('EQX1466', 'Crane', 'Available'),
            ('EQX1467', 'Crane', 'Available'),
            ('EQX1468', 'Crane', 'Available'),
            ('EQX1469', 'Crane', 'Available'),
            ('EQX1470', 'Crane', 'Available'),
            ('EQX1471', 'Crane', 'Available'),
            ('EQX1472', 'Crane', 'Available'),
            ('EQX1473', 'Crane', 'Available'),
            ('EQX1474', 'Crane', 'Available'),
            ('EQX1475', 'Crane', 'Available'),
            ('EQX1476', 'Crane', 'Available'),
            ('EQX1477', 'Crane', 'Available'),
            ('EQX1478', 'Crane', 'Available'),
            ('EQX1479', 'Crane', 'Available'),
            ('EQX1480', 'Crane', 'Available'),
            ('EQX1481', 'Crane', 'Available'),
            ('EQX1482', 'Crane', 'Available'),
            ('EQX1483', 'Crane', 'Available'),
            ('EQX1484', 'Crane', 'Available'),
            ('EQX1485', 'Crane', 'Available'),
            ('EQX1486', 'Crane', 'Available'),
            ('EQX1487', 'Crane', 'Available'),
            ('EQX1488', 'Crane', 'Available'),
            ('EQX1489', 'Crane', 'Available'),
            ('EQX1490', 'Crane', 'Available'),
            ('EQX1491', 'Crane', 'Available'),
            ('EQX1492', 'Crane', 'Available'),
            ('EQX1493', 'Crane', 'Available'),
            ('EQX1494', 'Crane', 'Available'),
            ('EQX1495', 'Crane', 'Available'),
            ('EQX1496', 'Crane', 'Available'),
            ('EQX1497', 'Crane', 'Available'),
            ('EQX1498', 'Crane', 'Available'),
            ('EQX1499', 'Crane', 'Available'),
            ('EQX1500', 'Crane', 'Available'),
            ('EQX1501', 'Bulldozer', 'Available'),
            ('EQX1502', 'Bulldozer', 'Available'),
            ('EQX1503', 'Bulldozer', 'Available'),
            ('EQX1504', 'Bulldozer', 'Available'),
            ('EQX1505', 'Bulldozer', 'Available'),
            ('EQX1506', 'Bulldozer', 'Available'),
            ('EQX1507', 'Bulldozer', 'Available'),
            ('EQX1508', 'Bulldozer', 'Available'),
            ('EQX1509', 'Bulldozer', 'Available'),
            ('EQX1510', 'Bulldozer', 'Available'),
            ('EQX1511', 'Bulldozer', 'Available'),
            ('EQX1512', 'Bulldozer', 'Available'),
            ('EQX1513', 'Bulldozer', 'Available'),
            ('EQX1514', 'Bulldozer', 'Available'),
            ('EQX1515', 'Bulldozer', 'Available'),
            ('EQX1516', 'Bulldozer', 'Available'),
            ('EQX1517', 'Bulldozer', 'Available'),
            ('EQX1518', 'Bulldozer', 'Available'),
            ('EQX1519', 'Bulldozer', 'Available'),
            ('EQX1520', 'Bulldozer', 'Available'),
            ('EQX1521', 'Bulldozer', 'Available'),
            ('EQX1522', 'Bulldozer', 'Available'),
            ('EQX1523', 'Bulldozer', 'Available'),
            ('EQX1524', 'Bulldozer', 'Available'),
            ('EQX1525', 'Bulldozer', 'Available'),
            ('EQX1526', 'Bulldozer', 'Available'),
            ('EQX1527', 'Bulldozer', 'Available'),
            ('EQX1528', 'Bulldozer', 'Available'),
            ('EQX1529', 'Bulldozer', 'Available'),
            ('EQX1530', 'Bulldozer', 'Available'),
            ('EQX1531', 'Bulldozer', 'Available'),
            ('EQX1532', 'Bulldozer', 'Available'),
            ('EQX1533', 'Bulldozer', 'Available'),
            ('EQX1534', 'Bulldozer', 'Available'),
            ('EQX1535', 'Bulldozer', 'Available'),
            ('EQX1536', 'Bulldozer', 'Available'),
            ('EQX1537', 'Bulldozer', 'Available'),
            ('EQX1538', 'Bulldozer', 'Available'),
            ('EQX1539', 'Bulldozer', 'Available'),
            ('EQX1540', 'Bulldozer', 'Available'),
            ('EQX1541', 'Bulldozer', 'Available'),
            ('EQX1542', 'Bulldozer', 'Available'),
            ('EQX1543', 'Bulldozer', 'Available'),
            ('EQX1544', 'Bulldozer', 'Available'),
            ('EQX1545', 'Bulldozer', 'Available'),
            ('EQX1546', 'Bulldozer', 'Available'),
            ('EQX1547', 'Bulldozer', 'Available'),
            ('EQX1548', 'Bulldozer', 'Available'),
            ('EQX1549', 'Bulldozer', 'Available'),
            ('EQX1550', 'Bulldozer', 'Available'),
            ('EQX1551', 'Bulldozer', 'Available'),
            ('EQX1552', 'Bulldozer', 'Available'),
            ('EQX1553', 'Bulldozer', 'Available'),
            ('EQX1554', 'Bulldozer', 'Available'),
            ('EQX1555', 'Bulldozer', 'Available'),
            ('EQX1556', 'Bulldozer', 'Available'),
            ('EQX1557', 'Bulldozer', 'Available'),
            ('EQX1558', 'Bulldozer', 'Available'),
            ('EQX1559', 'Bulldozer', 'Available'),
            ('EQX1560', 'Bulldozer', 'Available'),
            ('EQX1561', 'Bulldozer', 'Available'),
            ('EQX1562', 'Bulldozer', 'Available'),
            ('EQX1563', 'Bulldozer', 'Available'),
            ('EQX1564', 'Bulldozer', 'Available'),
            ('EQX1565', 'Bulldozer', 'Available'),
            ('EQX1566', 'Bulldozer', 'Available'),
            ('EQX1567', 'Bulldozer', 'Available'),
            ('EQX1568', 'Bulldozer', 'Available'),
            ('EQX1569', 'Bulldozer', 'Available'),
            ('EQX1570', 'Bulldozer', 'Available'),
            ('EQX1571', 'Bulldozer', 'Available'),
            ('EQX1572', 'Bulldozer', 'Available'),
            ('EQX1573', 'Bulldozer', 'Available'),
            ('EQX1574', 'Bulldozer', 'Available'),
            ('EQX1575', 'Bulldozer', 'Available'),
            ('EQX1576', 'Bulldozer', 'Available'),
            ('EQX1577', 'Bulldozer', 'Available'),
            ('EQX1578', 'Bulldozer', 'Available'),
            ('EQX1579', 'Bulldozer', 'Available'),
            ('EQX1580', 'Bulldozer', 'Available'),
            ('EQX1581', 'Bulldozer', 'Available'),
            ('EQX1582', 'Bulldozer', 'Available'),
            ('EQX1583', 'Bulldozer', 'Available'),
            ('EQX1584', 'Bulldozer', 'Available'),
            ('EQX1585', 'Bulldozer', 'Available'),
            ('EQX1586', 'Bulldozer', 'Available'),
            ('EQX1587', 'Bulldozer', 'Available'),
            ('EQX1588', 'Bulldozer', 'Available'),
            ('EQX1589', 'Bulldozer', 'Available'),
            ('EQX1590', 'Bulldozer', 'Available'),
            ('EQX1591', 'Bulldozer', 'Available'),
            ('EQX1592', 'Bulldozer', 'Available'),
            ('EQX1593', 'Bulldozer', 'Available'),
            ('EQX1594', 'Bulldozer', 'Available'),
            ('EQX1595', 'Bulldozer', 'Available'),
            ('EQX1596', 'Bulldozer', 'Available'),
            ('EQX1597', 'Bulldozer', 'Available'),
            ('EQX1598', 'Bulldozer', 'Available'),
            ('EQX1599', 'Bulldozer', 'Available'),
            ('EQX1600', 'Bulldozer', 'Available'),
            ('EQX1751', 'Grader', 'Available'),
            ('EQX1752', 'Grader', 'Available'),
            ('EQX1753', 'Grader', 'Available'),
            ('EQX1754', 'Grader', 'Available'),
            ('EQX1755', 'Grader', 'Available'),
            ('EQX1756', 'Grader', 'Available'),
            ('EQX1757', 'Grader', 'Available'),
            ('EQX1758', 'Grader', 'Available'),
            ('EQX1759', 'Grader', 'Available'),
            ('EQX1760', 'Grader', 'Available'),
            ('EQX1761', 'Grader', 'Available'),
            ('EQX1762', 'Grader', 'Available'),
            ('EQX1763', 'Grader', 'Available'),
            ('EQX1764', 'Grader', 'Available'),
            ('EQX1765', 'Grader', 'Available'),
            ('EQX1766', 'Grader', 'Available'),
            ('EQX1767', 'Grader', 'Available'),
            ('EQX1768', 'Grader', 'Available'),
            ('EQX1769', 'Grader', 'Available'),
            ('EQX1770', 'Grader', 'Available'),
            ('EQX1771', 'Grader', 'Available'),
            ('EQX1772', 'Grader', 'Available'),
            ('EQX1773', 'Grader', 'Available'),
            ('EQX1774', 'Grader', 'Available'),
            ('EQX1775', 'Grader', 'Available'),
            ('EQX1776', 'Grader', 'Available'),
            ('EQX1777', 'Grader', 'Available'),
            ('EQX1778', 'Grader', 'Available'),
            ('EQX1779', 'Grader', 'Available'),
            ('EQX1780', 'Grader', 'Available'),
            ('EQX1781', 'Grader', 'Available'),
            ('EQX1782', 'Grader', 'Available'),
            ('EQX1783', 'Grader', 'Available'),
            ('EQX1784', 'Grader', 'Available'),
            ('EQX1785', 'Grader', 'Available'),
            ('EQX1786', 'Grader', 'Available'),
            ('EQX1787', 'Grader', 'Available'),
            ('EQX1788', 'Grader', 'Available'),
            ('EQX1789', 'Grader', 'Available'),
            ('EQX1790', 'Grader', 'Available'),
            ('EQX1791', 'Grader', 'Available'),
            ('EQX1792', 'Grader', 'Available'),
            ('EQX1793', 'Grader', 'Available'),
            ('EQX1794', 'Grader', 'Available'),
            ('EQX1795', 'Grader', 'Available'),
            ('EQX1796', 'Grader', 'Available'),
            ('EQX1797', 'Grader', 'Available'),
            ('EQX1798', 'Grader', 'Available'),
            ('EQX1799', 'Grader', 'Available'),
            ('EQX1800', 'Grader', 'Available'),
            ('EQX1801', 'Grader', 'Available'),
            ('EQX1802', 'Grader', 'Available'),
            ('EQX1803', 'Grader', 'Available'),
            ('EQX1804', 'Grader', 'Available'),
            ('EQX1805', 'Grader', 'Available'),
            ('EQX1806', 'Grader', 'Available'),
            ('EQX1807', 'Grader', 'Available'),
            ('EQX1808', 'Grader', 'Available'),
            ('EQX1809', 'Grader', 'Available'),
            ('EQX1810', 'Grader', 'Available'),
            ('EQX1811', 'Grader', 'Available'),
            ('EQX1812', 'Grader', 'Available'),
            ('EQX1813', 'Grader', 'Available'),
            ('EQX1814', 'Grader', 'Available'),
            ('EQX1815', 'Grader', 'Available'),
            ('EQX1816', 'Grader', 'Available'),
            ('EQX1817', 'Grader', 'Available'),
            ('EQX1818', 'Grader', 'Available'),
            ('EQX1819', 'Grader', 'Available'),
            ('EQX1820', 'Grader', 'Available'),
            ('EQX1821', 'Grader', 'Available'),
            ('EQX1822', 'Grader', 'Available'),
            ('EQX1823', 'Grader', 'Available'),
            ('EQX1824', 'Grader', 'Available'),
            ('EQX1825', 'Grader', 'Available'),
            ('EQX1826', 'Grader', 'Available'),
            ('EQX1827', 'Grader', 'Available'),
            ('EQX1828', 'Grader', 'Available'),
            ('EQX1829', 'Grader', 'Available'),
            ('EQX1830', 'Grader', 'Available'),
            ('EQX1831', 'Grader', 'Available'),
            ('EQX1832', 'Grader', 'Available'),
            ('EQX1833', 'Grader', 'Available'),
            ('EQX1834', 'Grader', 'Available'),
            ('EQX1835', 'Grader', 'Available'),
            ('EQX1836', 'Grader', 'Available'),
            ('EQX1837', 'Grader', 'Available'),
            ('EQX1838', 'Grader', 'Available'),
            ('EQX1839', 'Grader', 'Available'),
            ('EQX1840', 'Grader', 'Available'),
            ('EQX1841', 'Grader', 'Available'),
            ('EQX1842', 'Grader', 'Available'),
            ('EQX1843', 'Grader', 'Available'),
            ('EQX1844', 'Grader', 'Available'),
            ('EQX1845', 'Grader', 'Available'),
            ('EQX1846', 'Grader', 'Available'),
            ('EQX1847', 'Grader', 'Available'),
            ('EQX1848', 'Grader', 'Available'),
            ('EQX1849', 'Grader', 'Available'),
            ('EQX1850', 'Grader', 'Available')
        ]
        
        backfill_demo_site_ids()

        cursor.executemany("""
        INSERT INTO Vendor (EquipmentID, Type, Availability)
        VALUES (?, ?, ?)
        """, equipment_list)

        conn.commit()
        print("✅ Vendor table pre-populated with default equipment data.")

    conn.close()


def add_rental_request(equipment_id: str, requester_site_id: int, location: str, time_from: str, time_to: str):
    with get_connection() as conn:
        cur = conn.execute("SELECT SiteID FROM Vendor WHERE EquipmentID = ?", (equipment_id,))
        row = cur.fetchone()
        owner_site_id = row[0] if row else None

        if owner_site_id is None:
            raise ValueError(f"Owner site not set for {equipment_id}. Please assign SiteID to this equipment.")

        if owner_site_id == requester_site_id:
            raise ValueError("You cannot request your own equipment.")

        conn.execute(
            "INSERT INTO RentalRequests (EquipmentID, RequesterSiteID, OwnerSiteID, Location, TimeFrom, TimeTo) "
            "VALUES (?,?,?,?,?,?)",
            (equipment_id, requester_site_id, owner_site_id, location, time_from, time_to)
        )
        conn.commit()


def get_requests_for_owner(site_id: int) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT RequestID, EquipmentID, RequesterSiteID, OwnerSiteID, Location, TimeFrom, TimeTo, Status
            FROM RentalRequests
            WHERE OwnerSiteID = ? AND Status = 'Pending'
            ORDER BY RequestID DESC
            """,
            conn, params=(site_id,)
        )

def approve_request(request_id: int, requester_site_id: int, equipment_id: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE RentalRequests SET Status='Approved' WHERE RequestID=?", (request_id,))
        cur.execute("UPDATE Vendor SET SharedBySiteID=?, ReadyToShare=0 WHERE EquipmentID=?",
                    (requester_site_id, equipment_id))
        conn.commit()

def update_request_status(request_id: int, status: str, requester_site_id: int):
    with get_connection() as conn:
        cur = conn.cursor()

        # Update request status
        cur.execute(
            "UPDATE RentalRequests SET Status = ? WHERE RequestID = ?",
            (status, request_id)
        )

        # Store RequestID in Vendor table for the related equipment
        cur.execute(
            """
            UPDATE Vendor
            SET SharedBySiteID = ?
            WHERE EquipmentID = (
                SELECT EquipmentID FROM RentalRequests WHERE RequestID = ?
            )
            """,
            (requester_site_id, request_id)
        )

        conn.commit()



###################


def insert_site(site_id, location, contact, equipment_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO SiteInfo (SiteID, EquipmentID, Location, ContactDetails) VALUES (?, ?, ?, ?)",
        (site_id, equipment_id, location, contact)
    )
    conn.commit()
    conn.close()



def insert_vendor(equipment_id, type_, site_id, operating_days, location, start_date, rental_type, availability="Available"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Vendor (
            EquipmentID, Type, SiteID, OperatingDays, Location,
            CheckOutDate, Availability, RentalType
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (equipment_id, type_, site_id, operating_days, location, start_date, availability, rental_type))
    conn.commit()
    conn.close()



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

# Update usage (engine + idle hours) for rented equipment
def update_usage(equipment_id, engine_hours, idle_hours):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Vendor
            SET 
                EngineHourDay = (COALESCE(EngineHourDay, 0) + ?) % 24,
                IdleHourDay   = (COALESCE(IdleHourDay, 0) + ?) % 24
            WHERE EquipmentID = ? AND Availability = 'Rented';
    """, (engine_hours, idle_hours, equipment_id))
    conn.commit()
    conn.close()

import time
import random

def simulate_realtime_updates():
    while True:
        rented_ids = fetch_vendors(filter_by="Rented") 
        equipment_ids = [row[0] for row in rented_ids]
        if equipment_ids:
            # Pick a random rented equipment
            eq_id = random.choice(equipment_ids)
            
            # Fake sensor data (hours used in last interval)
            engine_hours = round(random.uniform(0.1, 1.0), 2)
            idle_hours   = round(random.uniform(0.0, 0.5), 2)

            update_usage(eq_id, engine_hours, idle_hours)
            print(f"Updated {eq_id}: +{engine_hours} engine hr, +{idle_hours} idle hr")

        time.sleep(2)  # wait 2 sec like real-time stream

def update_fuel(equipment_id, fuel):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Vendor
        SET Fuel = ?
        WHERE EquipmentID = ? AND Availability = 'Rented'
    """, (fuel, equipment_id))
    conn.commit()
    conn.close()

def mark_ready_to_share(equipment_id: str, ready: bool, shared_by_site_id: int | None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Vendor SET ReadyToShare=?, SharedBySiteID=? WHERE EquipmentID=?",
        (1 if ready else 0, shared_by_site_id if ready else None, equipment_id),
    )
    conn.commit()
    conn.close()

def fetch_share_ready(exclude_site_id: int | None = None):
    ensure_vendor_share_columns()  # make sure columns exist
    conn = get_connection()
    cur = conn.cursor()
    try:
        if exclude_site_id is None:
            cur.execute("SELECT * FROM Vendor WHERE ReadyToShare=1")
        else:
            cur.execute("SELECT * FROM Vendor WHERE ReadyToShare=1 AND SiteID<>?", (exclude_site_id,))
        return cur.fetchall()
    finally:
        conn.close()


# --- add near your other DB helpers ---
def ensure_vendor_share_columns():
    """
    Ensures Vendor table exists and has:
      - RentalType TEXT CHECK(RentalType IN ('Rigid','Flexible'))
      - ReadyToShare INTEGER DEFAULT 0
      - SharedBySiteID INTEGER
    (Won't destroy existing data.)
    """
    with get_connection() as conn:
        cur = conn.cursor()

        # Create if missing (matches your schema)
        cur.execute("""
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
                RentalType TEXT CHECK(RentalType IN ('Rigid', 'Flexible')),
                ReadyToShare INTEGER DEFAULT 0,
                SharedBySiteID INTEGER
            )
        """)

        # Make sure columns exist even if table was older
        cur.execute("PRAGMA table_info(Vendor)")
        existing = {row[1] for row in cur.fetchall()}

        if "RentalType" not in existing:
            cur.execute("ALTER TABLE Vendor ADD COLUMN RentalType TEXT")
        if "ReadyToShare" not in existing:
            cur.execute("ALTER TABLE Vendor ADD COLUMN ReadyToShare INTEGER DEFAULT 0")
        if "SharedBySiteID" not in existing:
            cur.execute("ALTER TABLE Vendor ADD COLUMN SharedBySiteID INTEGER")
        conn.commit()

def get_flexible_rentals() -> pd.DataFrame:
    """
    Fetch Flexible rentals from Vendor, tolerant to case/spacing.
    """
    with get_connection() as conn:
        q = """
        SELECT
            EquipmentID,
            Type,
            SiteID,
            CheckOutDate,
            CheckInDate,
            EngineHourDay,
            IdleHourDay,
            OperatingDays,
            DaysLeft,
            Fuel,
            Location,
            Availability,
            RentalType,
            ReadyToShare,
            SharedBySiteID
        FROM Vendor
        WHERE TRIM(LOWER(COALESCE(RentalType,''))) = 'flexible'
        """
        return pd.read_sql_query(q, conn)

def set_ready_to_share(equipment_id: str, value: int = 1, shared_by_site_id: int | None = None):
    """
    Toggle ReadyToShare. When enabling, also set SharedBySiteID (if provided).
    When disabling, clear SharedBySiteID.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        if int(value) == 1:
            # If caller didn’t pass a site, keep existing
            cur.execute(
                "UPDATE Vendor SET ReadyToShare = 1, SharedBySiteID = COALESCE(?, SharedBySiteID) WHERE EquipmentID = ?",
                (shared_by_site_id, equipment_id)
            )
        else:
            cur.execute(
                "UPDATE Vendor SET ReadyToShare = 0, SharedBySiteID = NULL WHERE EquipmentID = ?",
                (equipment_id,)
            )
        conn.commit()


def get_all_rental_requests() -> pd.DataFrame:
    """
    Fetch all RentalRequests rows for debugging/inspection.
    """
    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM RentalRequests ORDER BY RequestID DESC", conn)