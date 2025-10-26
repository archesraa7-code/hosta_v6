import streamlit as st
from db import _conn, add_booking

# اللغة
if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"

rtl = (st.session_state["lang"] == "ar")

if rtl:
    st.markdown("""
    <style>
    html, body, [class^='css']{ direction: RTL; text-align:right; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏨 الحجوزات" if rtl else "🏨 Bookings")

conn = _conn()

clients = conn.execute("SELECT id, name FROM clients").fetchall()
hotels = conn.execute("SELECT id, name_ar, name_en FROM hotels").fetchall()
restaurants = conn.execute("SELECT id, name_ar, name_en, type FROM restaurants").fetchall()

with st.form("new_booking", clear_on_submit=True):
    st.subheader("➕ إضافة حجز جديد" if rtl else "➕ Add New Booking")

    col1, col2, col3 = st.columns(3)

    with col1:
        client = st.selectbox("العميل" if rtl else "Client", clients, format_func=lambda x: x["name"])
        hotel = st.selectbox("الفندق" if rtl else "Hotel", hotels,
                             format_func=lambda x: x["name_ar"] if rtl else x["name_en"])
        pax = st.number_input("عدد الأشخاص" if rtl else "PAX", min_value=1, step=1)

    with col2:
        checkin = st.date_input("الدخول" if rtl else "Check-in")
        checkout = st.date_input("الخروج" if rtl else "Check-out")
        rooms = st.number_input("عدد الغرف" if rtl else "Rooms", min_value=1, step=1)

    with col3:
        room_cost = st.number_input("تكلفة الغرفة/ليلة" if rtl else "Room Cost/Night", min_value=0.0)
        room_price = st.number_input("سعر بيع الغرفة/ليلة" if rtl else "Room Price/Night", min_value=0.0)

    st.markdown("---")

    restaurant_mode = st.selectbox("نظام الوجبات" if rtl else "Meal Mode",
                                   ["none","full_kitchen","chair_fee"],
                                   format_func=lambda x: {"none":"بدون","full_kitchen":"مطبخ خارجي","chair_fee":"كرسي"}[x] if rtl else x)

    restaurant_id = None

    if restaurant_mode == "full_kitchen":
        restaurant = st.selectbox("المطعم" if rtl else "Restaurant",
                                  restaurants,
                                  format_func=lambda x: x["name_ar"] if rtl else x["name_en"])
        restaurant_id = restaurant["id"]
        meal_cost = st.number_input("تكلفة 3 وجبات/فرد/يوم" if rtl else "Meal Cost/Person/Day", min_value=0.0)
        meal_price = st.number_input("سعر بيع الوجبات" if rtl else "Meal Sell Price", min_value=0.0)
        chair_price = 0

    elif restaurant_mode == "chair_fee":
        meal_cost = 0
        meal_price = 0
        chair_price = st.number_input("سعر الكرسي/فرد/يوم" if rtl else "Chair Fee/Person/Day", min_value=0.0)

    else:
        meal_cost = 0
        meal_price = 0
        chair_price = 0

    paid = st.number_input("مدفوع من العميل" if rtl else "Paid by Client", min_value=0.0, step=1.0)
    notes = st.text_area("ملاحظات" if rtl else "Notes")

    submitted = st.form_submit_button("حفظ ✅" if rtl else "Save ✅")

    if submitted:
        data = dict(
            code=None,
            client_id=client["id"],
            hotel_id=hotel["id"],
            restaurant_id=restaurant_id,
            checkin=str(checkin),
            checkout=str(checkout),
            rooms=rooms,
            pax=pax,
            room_cost=room_cost,
            room_price=room_price,
            meal_cost=meal_cost,
            meal_price=meal_price,
            chair_price=chair_price,
            restaurant_mode=restaurant_mode,
            paid=paid,
            notes=notes
        )
        add_booking(data)
        st.success("✅ تم تسجيل الحجز ومعالجته محاسبيًا" if rtl else "✅ Booking saved with full accounting processing")
        st.experimental_rerun()

st.write("---")
st.write("🧾 آخر الحجوزات" if rtl else "🧾 Recent Bookings")

rows = conn.execute("""
SELECT b.code, c.name, h.name_ar, b.checkin, b.checkout, b.rooms, b.pax
FROM bookings b
LEFT JOIN clients c ON c.id=b.client_id
LEFT JOIN hotels h ON h.id=b.hotel_id
ORDER BY b.id DESC LIMIT 12
""").fetchall()

for r in rows:
    st.write(f"**{r[0]}** | {r[1]} | {r[2]} | {r[3]} → {r[4]} | {r[5]} غرفة | {r[6]} شخص")
