import sqlite3
from datetime import datetime

# -------------------------------------------------
# اتصال بالقائمة
# -------------------------------------------------
def _conn():
    conn = sqlite3.connect("hotel.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------------------------
# إنشاء الجداول
# -------------------------------------------------
_conn().executescript("""
CREATE TABLE IF NOT EXISTS clients(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hotels(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name_ar TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS restaurants(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name_ar TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER,
 hotel_id INTEGER,
 restaurant_id INTEGER,
 rooms INTEGER,
 pax INTEGER,
 checkin TEXT,
 checkout TEXT,
 room_price REAL,
 meal_price REAL,
 notes TEXT,
 FOREIGN KEY(client_id) REFERENCES clients(id),
 FOREIGN KEY(hotel_id) REFERENCES hotels(id),
 FOREIGN KEY(restaurant_id) REFERENCES restaurants(id)
);

-- دفتر الأستاذ المالي (Ledger)
CREATE TABLE IF NOT EXISTS ledger(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 ref_type TEXT,
 ref_id INTEGER,
 party_type TEXT,
 party_id INTEGER,
 amount REAL,
 direction TEXT, -- debit or credit
 date TEXT,
 notes TEXT
);

""")

# -------------------------------------------------
# دوال مساعدة
# -------------------------------------------------

def add_client(name):
    _conn().execute("INSERT INTO clients(name) VALUES(?)", (name,))
    _conn().commit()

def add_hotel(name):
    _conn().execute("INSERT INTO hotels(name_ar) VALUES(?)", (name,))
    _conn().commit()

def add_restaurant(name):
    _conn().execute("INSERT INTO restaurants(name_ar) VALUES(?)", (name,))
    _conn().commit()

# -------------------------------------------------
# إضافة حجز + تسجيله محاسبيًا
# -------------------------------------------------
def add_booking(client_id, hotel_id, restaurant_id, rooms, pax, checkin, checkout, room_price, meal_price, notes):
    conn = _conn()
    conn.execute("""
        INSERT INTO bookings(client_id, hotel_id, restaurant_id, rooms, pax, checkin, checkout, room_price, meal_price, notes)
        VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (client_id, hotel_id, restaurant_id, rooms, pax, checkin, checkout, room_price, meal_price, notes))
    booking_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    total = (rooms * room_price) + (pax * meal_price)
    date = datetime.now().strftime("%Y-%m-%d")

    conn.execute("""
        INSERT INTO ledger(ref_type, ref_id, party_type, party_id, amount, direction, date, notes)
        VALUES('booking', ?, 'client', ?, ?, 'debit', ?, ?)
    """, (booking_id, client_id, total, date, "قيمة الحجز"))

    conn.commit()
    return booking_id

# -------------------------------------------------
# سند قبض (تسديد من العميل)
# -------------------------------------------------
def add_receipt(client_id, amount, notes):
    date = datetime.now().strftime("%Y-%m-%d")
    _conn().execute("""
        INSERT INTO ledger(ref_type, party_type, party_id, amount, direction, date, notes)
        VALUES('receipt', 'client', ?, ?, 'credit', ?, ?)
    """, (client_id, amount, date, notes))
    _conn().commit()

# -------------------------------------------------
# سند صرف (مصروفات على العميل / الفندق / المطعم)
# -------------------------------------------------
def add_payment(party_type, party_id, amount, notes):
    date = datetime.now().strftime("%Y-%m-%d")
    _conn().execute("""
        INSERT INTO ledger(ref_type, party_type, party_id, amount, direction, date, notes)
        VALUES('payment', ?, ?, ?, 'debit', ?, ?)
    """, (party_type, party_id, amount, date, notes))
    _conn().commit()

# -------------------------------------------------
# رصيد أي طرف Client / Hotel / Restaurant / Delegate
# -------------------------------------------------
def get_balance(party_type, party_id):
    conn = _conn()
    debit = conn.execute("SELECT SUM(amount) FROM ledger WHERE party_type=? AND party_id=? AND direction='debit'", (party_type, party_id)).fetchone()[0] or 0
    credit = conn.execute("SELECT SUM(amount) FROM ledger WHERE party_type=? AND party_id=? AND direction='credit'", (party_type, party_id)).fetchone()[0] or 0
    return debit - credit

# -------------------------------------------------
# كشف حساب
# -------------------------------------------------
def get_statement(party_type, party_id):
    return _conn().execute("""
        SELECT date, notes, direction, amount
        FROM ledger
        WHERE party_type=? AND party_id=?
        ORDER BY id DESC
    """, (party_type, party_id)).fetchall()
