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

st.title("🍽️ مستحقات المطاعم" if rtl else "🍽️ Restaurant Balances")

conn = _conn()

rows = conn.execute("SELECT id, name_ar FROM restaurants").fetchall()

data = []
for r in rows:
    bal = party_balance("restaurant", r["id"])
    data.append({
        ("المطعم" if rtl else "Restaurant"): r["name_ar"],
        ("الرصيد (ر.س)" if rtl else "Balance (SAR)"): f"{bal:,.2f}"
    })

st.table(data)
