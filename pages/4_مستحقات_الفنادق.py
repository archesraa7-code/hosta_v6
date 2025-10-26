import streamlit as st
from db import _conn, party_balance

if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"

rtl = (st.session_state["lang"] == "ar")

if rtl:
    st.markdown("""
    <style>
    html, body, [class^='css']{ direction:RTL; text-align:right; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏨 مستحقات الفنادق" if rtl else "🏨 Hotel Balances")

conn = _conn()

rows = conn.execute("""
SELECT id, name_ar FROM hotels
""").fetchall()

data = []
for r in rows:
    bal = party_balance("hotel", r["id"])
    data.append({"الفندق" if rtl else "Hotel": r["name_ar"], 
                 "الرصيد (ر.س)" if rtl else "Balance (SAR)": f"{bal:,.2f}"})

st.table(data)
