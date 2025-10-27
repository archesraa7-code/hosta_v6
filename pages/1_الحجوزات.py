import streamlit as st
from datetime import date
from db import _conn, add_booking

st.title("🏨 إدارة الحجوزات")

conn = _conn()

# -----------------------------
# تحميل القوائم من قاعدة البيانات (أسماء الأعمدة: name)
# -----------------------------
def load_lists():
    customers = conn.execute("SELECT id, name FROM customers ORDER BY name").fetchall()
    hotels    = conn.execute("SELECT id, name FROM hotels ORDER BY name").fetchall()
    rests     = conn.execute("SELECT id, name FROM restaurants ORDER BY name").fetchall()
    return customers, hotels, rests

customers, hotels, restaurants = load_lists()

# -----------------------------
# إضافة سريعــة (عميل / فندق / مطعم)
# -----------------------------
with st.expander("➕ إضافة عميل / فندق / مطعم"):
    c1, c2, c3 = st.columns(3)
    with c1:
        new_cust = st.text_input("اسم العميل / الشركة", key="new_cust")
        if st.button("إضافة عميل", key="btn_add_cust") and new_cust.strip():
            conn.execute("INSERT INTO customers(name) VALUES (?)", (new_cust.strip(),))
            conn.commit()
            st.success("تمت إضافة العميل ✅")
            customers, hotels, restaurants = load_lists()

    with c2:
        new_hotel = st.text_input("اسم الفندق", key="new_hotel")
        if st.button("إضافة فندق", key="btn_add_hotel") and new_hotel.strip():
            conn.execute("INSERT INTO hotels(name) VALUES (?)", (new_hotel.strip(),))
            conn.commit()
            st.success("تمت إضافة الفندق ✅")
            customers, hotels, restaurants = load_lists()

    with c3:
        new_rest = st.text_input("اسم المطعم", key="new_rest")
        if st.button("إضافة مطعم", key="btn_add_rest") and new_rest.strip():
            conn.execute("INSERT INTO restaurants(name) VALUES (?)", (new_rest.strip(),))
            conn.commit()
            st.success("تمت إضافة المطعم ✅")
            customers, hotels, restaurants = load_lists()

# -----------------------------
# نموذج إضافة حجز
# -----------------------------
st.subheader("📝 إضافة حجز جديد")

client_options = [("اختر العميل", None)] + [(c["name"], c["id"]) for c in customers]
hotel_options  = [("اختر الفندق", None)] + [(h["name"], h["id"]) for h in hotels]
rest_options   = [("بدون مطعم", None)] + [(r["name"], r["id"]) for r in restaurants]

sel_client = st.selectbox("العميل", client_options, index=0, key="sel_client",
                          format_func=lambda x: x[0] if x else "")
sel_hotel  = st.selectbox("الفندق", hotel_options,  index=0, key="sel_hotel",
                          format_func=lambda x: x[0] if x else "")
sel_rest   = st.selectbox("المطعم (اختياري)", rest_options, index=0, key="sel_rest",
                          format_func=lambda x: x[0] if x else "")

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    rooms = st.number_input("عدد الغرف", min_value=1, step=1, key="rooms")
with col_b:
    pax = st.number_input("عدد الأشخاص", min_value=1, step=1, key="pax")
with col_c:
    checkin = st.date_input("تاريخ الدخول", value=date.today(), key="in_date")
with col_d:
    checkout = st.date_input("تاريخ الخروج", value=date.today(), key="out_date")

col_p, col_m = st.columns(2)
with col_p:
    room_price = st.number_input("سعر الغرفة لليلة (ر.س)", min_value=0.0, step=1.0, key="room_price")
with col_m:
    meal_price = st.number_input("سعر الوجبات للفرد/اليوم (اختياري)", min_value=0.0, step=1.0, key="meal_price")

notes = st.text_area("ملاحظات", key="notes")

# -----------------------------
# حساب تلقائي
# -----------------------------
days = (checkout - checkin).days
if days < 1:
    st.warning("⚠️ يجب أن يكون تاريخ الخروج بعد تاريخ الدخول بيوم واحد على الأقل.")
else:
    total_rooms = rooms * room_price * days
    total_meals = pax * meal_price * days
    total = total_rooms + total_meals

    st.info(
        f"**عدد الليالي:** {days}  \n"
        f"**إجمالي الغرف:** {total_rooms:,.2f} ر.س  \n"
        f"**إجمالي الوجبات:** {total_meals:,.2f} ر.س  \n"
        f"### **الإجمالي النهائي: {total:,.2f} ر.س**"
    )

# -----------------------------
# حفظ الحجز
# -----------------------------
if st.button("💾 حفظ الحجز", key="save_booking"):
    if not sel_client[1] or not sel_hotel[1]:
        st.error("❗ يجب اختيار العميل والفندق.")
    elif days < 1:
        st.error("❗ تاريخ الخروج غير صحيح.")
    else:
        booking_id = add_booking(
            client_id=sel_client[1],
            hotel_id=sel_hotel[1],
            restaurant_id=sel_rest[1] if sel_rest and sel_rest[1] else None,
            rooms=int(rooms),
            pax=int(pax),
            checkin=str(checkin),
            checkout=str(checkout),
            room_price=float(room_price),
            meal_price=float(meal_price),
            notes=notes.strip()
        )
        st.success(f"✅ تم تسجيل الحجز بنجاح (رقم الحجز: {booking_id})")
