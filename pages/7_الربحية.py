import streamlit as st
from db import _conn

if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"

rtl = (st.session_state["lang"] == "ar")

if rtl:
    st.markdown("""
    <style>
    html, body, [class^='css']{ direction:RTL; text-align:right; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 الربحية" if rtl else "📊 Profit Dashboard")

conn = _conn()

# إجمالي المبيعات للعملاء
sales = conn.execute("""
SELECT COALESCE(SUM(credit),0) FROM ledger WHERE party_type='client'
""").fetchone()[0]

# إجمالي التكاليف للفنادق + المطاعم
costs = conn.execute("""
SELECT COALESCE(SUM(debit),0) FROM ledger WHERE party_type IN ('hotel','restaurant')
""").fetchone()[0]

# إجمالي مصروفات التشغيل
expenses = conn.execute("""
SELECT COALESCE(SUM(debit),0) FROM ledger WHERE party_type='expense'
""").fetchone()[0]

profit = sales - costs - expenses
margin = (profit / sales * 100) if sales else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💵 إجمالي المبيعات" if rtl else "Total Sales", f"{sales:,.2f} ر.س")
col2.metric("🏨 التكاليف" if rtl else "Costs", f"{costs:,.2f} ر.س")
col3.metric("🧾 المصروفات" if rtl else "Operating Expenses", f"{expenses:,.2f} ر.س")
col4.metric("💰 صافي الربح" if rtl else "Net Profit", f"{profit:,.2f} ر.س")

st.markdown("---")

st.subheader("📈 هامش الربح" if rtl else "Profit Margin %")
st.progress(int(margin if margin > 0 else 0))
st.write(f"**{margin:.1f}%**")
