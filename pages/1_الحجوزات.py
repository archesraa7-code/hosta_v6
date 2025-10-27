import streamlit as st
from datetime import datetime
from db import _conn, add_booking, add_client, add_hotel, add_restaurant

st.title("🏨 إدارة الحجوزات")

conn = _conn()

# جلب بيانات القوائم
clients = conn.execute("SELECT id, name FROM customers").fetchall()
hotels = conn.execute("SELECT id, name as label FROM hotels").fetchall()
restaurants = conn.execute("SELECT id, name FROM restaurants").fetchall()

# ------------------------------
# إضافة عملاء / فنادق / مطاعم
# ------------------------------
with st.expander("➕ إضافة عميل / فندق / مطعم"):
    col1, col2, col3 = st.columns(3)

    with col1:
        new_client = st.text_input("اسم العميل / الشركة")
        if st.button("إضافة عميل"):
            add_client(new_client)
            st.success("تمت الإضافة ✅")
            st.experimental_rerun()

    with col2:
        new_hotel = st.text_input("اسم الفندق")
        if st.button("إضافة فندق"):
            add_hotel(new_hotel)
            st.success("تمت الإضافة ✅")
            st.experimental_rerun()

    with col3:
        new_rest = st.text_input("اسم المطعم")
        if st.button("إضافة مطعم"):
            add_restaurant(new_rest)
            st.success("تمت الإضافة ✅")
            st.experimental_rerun()

# ------------------------------
# نموذج الحجز
# ------------------------------
st.subheader("📝 إضافة حجز جديد")

client = st.selectbox("العميل", [("اختر",None)] + [(c["name"], c["id"]) for c in clients], format_func=lambda x: x[0] if x else "")
hotel = st.selectbox("الفندق", [("اختر",None)] + [(h["name_ar"], h["id"]) for h in hotels], format_func=lambda x: x[0] if x else "")
restaurant = st.selectbox("المطعم (اختياري)", [("بدون مطعم", None)] + [(r["name_ar"], r["id"]) for r in restaurants], format_func=lambda x: x[0] if x else "")

rooms = st.number_input("عدد الغرف", min_value=1, step=1)
pax = st.number_input("عدد الأشخاص", min_value=1, step=1)

checkin = st.date_input("تاريخ الدخول")
checkout = st.date_input("تاريخ الخروج")

room_price = st.number_input("سعر الغرفة لليلة (ريال)", min_value=0.0, step=1.0)
meal_price = st.number_input("سعر الوجبات للفرد باليوم (اختياري)", min_value=0.0, step=1.0)

notes = st.text_area("ملاحظات", "")

# حساب الليالي + الإجمالي
days = (checkout - checkin).days
if days < 1:
    st.warning("⚠️ تاريخ الخروج يجب أن يكون بعد الدخول")
else:
    total_rooms = rooms * room_price * days
    total_meals = pax * meal_price * days
    total = total_rooms + total_meals

    st.info(f"""
    **عدد الليالي:** {days}
    **إجمالي الغرف:** {total_rooms:,.2f} ر.س
    **إجمالي الوجبات:** {total_meals:,.2f} ر.س
    ### **الإجمالي النهائي: {total:,.2f} ر.س**
    """)

    if st.button("💾 حفظ الحجز"):
        if client[1] and hotel[1]:
            booking_id = add_booking(client[1], hotel[1], restaurant[1] if restaurant else None, rooms, pax, str(checkin), str(checkout), room_price, meal_price, notes)
            st.success(f"✅ تم تسجيل الحجز بنجاح (رقم الحجز: {booking_id})")
        else:
            st.error("❗ يجب اختيار العميل والفندق")
