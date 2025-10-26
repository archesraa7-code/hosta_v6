import sqlite3

conn = sqlite3.connect("hotel.db")
cur = conn.cursor()

# العملاء
cur.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT
)
""")

# الفنادق
cur.execute("""
CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ar TEXT NOT NULL,
    name_en TEXT,
    relation_type TEXT CHECK(relation_type IN ('supplier','mediator','catering')) DEFAULT 'supplier'
)
""")

# المطاعم
cur.execute("""
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ar TEXT NOT NULL,
    name_en TEXT,
    type TEXT CHECK(type IN('none','full_kitchen','chair_fee')) DEFAULT 'none'
)
""")

# المندوبين
cur.execute("""
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# الحجوزات الأساسية
cur.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    client_id INTEGER,
    hotel_id INTEGER,
    restaurant_id INTEGER,
    checkin TEXT,
    checkout TEXT,
    rooms INTEGER,
    pax INTEGER,
    room_cost REAL,
    room_price REAL,
    meal_cost REAL,
    meal_price REAL,
    chair_price REAL,
    restaurant_mode TEXT CHECK(restaurant_mode IN ('none','full_kitchen','chair_fee')) DEFAULT 'none',
    paid REAL DEFAULT 0,
    notes TEXT,
    FOREIGN KEY(client_id) REFERENCES clients(id),
    FOREIGN KEY(hotel_id) REFERENCES hotels(id),
    FOREIGN KEY(restaurant_id) REFERENCES restaurants(id)
)
""")

# تمديد الحجز
cur.execute("""
CREATE TABLE IF NOT EXISTS extensions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    nights INTEGER,
    rooms INTEGER,
    pax INTEGER,
    room_cost REAL,
    room_price REAL,
    meal_cost REAL,
    meal_price REAL,
    chair_price REAL,
    restaurant_mode TEXT CHECK(restaurant_mode IN ('none','full_kitchen','chair_fee')) DEFAULT 'none',
    created_at TEXT,
    FOREIGN KEY(booking_id) REFERENCES bookings(id) ON DELETE CASCADE
)
""")

# سجل محاسبي موحد
cur.execute("""
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    party_type TEXT,
    party_id INTEGER,
    ref_type TEXT,
    ref_code TEXT,
    description TEXT,
    debit REAL DEFAULT 0,
    credit REAL DEFAULT 0
)
""")

# المصروفات
cur.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    person TEXT,
    method TEXT,
    amount REAL,
    notes TEXT
)
""")

# سلف / عهدة مندوب
cur.execute("""
CREATE TABLE IF NOT EXISTS agent_cash (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER,
    ts TEXT,
    direction TEXT CHECK(direction IN ('in','out')),
    amount REAL,
    note TEXT,
    FOREIGN KEY(agent_id) REFERENCES agents(id)
)
""")

# المدفوعات للعميل
cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    amount REAL,
    date TEXT
)
""")

conn.commit()
conn.close()

print("✅ قاعدة البيانات جاهزة وتم إنشاؤها بالكامل")
