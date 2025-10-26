import streamlit as st
from db import _conn, get_balance, get_statement

st.title("📄 كشف حساب")

conn = _conn()

# اختيار النوع
party_type = st.selectbox("نوع الحساب", {
    "client": "عميل / شركة",
    "hotel": "فندق",
    "restaurant": "مطعم",
}.keys(), format_func=lambda x: {
    "client": "عميل / شركة",
    "hotel": "فندق",
    "restaurant": "مطعم",
}[x])

# جلب القائمة حسب الاختيار
if party_type == "client":
    parties = conn.execute("SELECT id, name as label FROM clients").fetchall()
elif party_type == "hotel":
    parties = conn.execute("SELECT id, name_ar as label FROM hotels").fetchall()
else:
    parties = conn.execute("SELECT id, name_ar as label FROM restaurants").fetchall()

party = st.selectbox("اختار الحساب", [(p["label"], p["id"]) for p in parties], format_func=lambda x: x[0])

if party:
    pid = party[1]

    balance = get_balance(party_type, pid)
    st.info(f"**الرصيد الحالي:** {balance:,.2f} ر.س")

    st.write("### الحركات")
    rows = get_statement(party_type, pid)

    for r in rows:
        direction = "مدين ➕" if r["direction"] == "debit" else "دائن ➖"
        st.write(f"""
        **التاريخ:** {r["date"]}
        - **البيان:** {r["notes"]}
        - **المبلغ:** {r["amount"]:,.2f} ر.س
        - **النوع:** {direction}
        ---
        """)
