import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="الحجوزات", page_icon="🛎️", layout="wide")

def get_conn():
    return sqlite3.connect("hotel.db")

st.markdown("<h2 style='text-align:right;'>🛎️ إدارة الحجوزات</h2>", unsafe_allow_html=True)
st.write("---")

with st.form("add_reservation", clear_on_submit=True):
    st.markdown("### ➕ إضافة حجز جديد")

    col1, col2, col3 = st.columns(3)

    with col1:
        customer = st.text_input("اسم العميل")
        hotel_name = st.text_input("اسم الفندق")
        room_count = st.number_input("عدد الغرف", min_value=1, step=1)

    with col2:
        check_in = st.date_input("تاريخ الدخول")
        check_out = st.date_input("تاريخ الخروج")
        price_per_night = st.number_input("سعر الغرفة لليوم", min_value=0.0, step=1.0)

    with col3:
        meal_cost = st.number_input("تكلفة الوجبات (اختياري)", min_value=0.0, step=1.0)
        notes = st.text_area("ملاحظات إضافية")

    submit = st.form_submit_button("حفظ الحجز ✅")

    if submit:
        nights = (check_out - check_in).days
        total_room_cost = room_count * price_per_night * nights
        total_cost = total_room_cost + meal_cost

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO reservations(customer, hotel_name, room_count, check_in, check_out, price_per_night, meal_cost, total_cost, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer, hotel_name, room_count, str(check_in), str(check_out), price_per_night, meal_cost, total_cost, notes))
        conn.commit()
        conn.close()

        st.success("✅ تم حفظ الحجز بنجاح")

st.write("### 📋 قائمة الحجوزات")
conn = get_conn()
rows = conn.execute("SELECT rowid, * FROM reservations ORDER BY rowid DESC").fetchall()
conn.close()

if rows:
    for r in rows:
        st.write(f"**رقم:** {r[0]} | **عميل:** {r[1]} | **فندق:** {r[2]} | **الإجمالي:** {r[8]} ريال")
else:
    st.info("لا يوجد حجوزات بعد.")
