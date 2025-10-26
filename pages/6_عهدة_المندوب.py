import streamlit as st
from db import _conn, add_agent_cash, party_balance

if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"

rtl = (st.session_state["lang"] == "ar")

if rtl:
    st.markdown("""
    <style>
    html, body, [class^='css']{ direction:RTL; text-align:right; }
    </style>
    """, unsafe_allow_html=True)

st.title("👤 عهدة المندوب" if rtl else "👤 Agent Cash")

conn = _conn()
agents = conn.execute("SELECT id,name FROM agents").fetchall()

agent = st.selectbox("اختر المندوب" if rtl else "Select Agent", agents, format_func=lambda x: x["name"])

st.write("---")
st.subheader("💰 تسجيل عملية جديدة" if rtl else "💰 New Transaction")

direction = st.radio(
    "نوع العملية" if rtl else "Transaction Type",
    ["out","in"],
    format_func=lambda x: {"out":"صرف للمندوب","in":"توريد من المندوب"}[x] if rtl else x,
    horizontal=True
)

amount = st.number_input("المبلغ (ر.س)" if rtl else "Amount (SAR)", min_value=0.0, step=1.0, format="%.2f")
note = st.text_input("بيان الحركة" if rtl else "Note")

if st.button("حفظ العملية ✅" if rtl else "Save ✅"):
    add_agent_cash(agent["id"], amount, direction, note)
    st.success("✅ تم تسجيل العملية" if rtl else "✅ Saved!")
    st.experimental_rerun()

st.write("---")
st.subheader("📊 الرصيد الحالي" if rtl else "📊 Current Balance")

balance = party_balance("agent", agent["id"])
st.info(f"{balance:,.2f} ر.س")

st.write("---")
st.subheader("🧾 سجل العهدة" if rtl else "🧾 Agent Ledger")

rows = conn.execute("""
SELECT ts, direction, amount, note
FROM agent_cash
WHERE agent_id = ?
ORDER BY datetime(ts) DESC
""", (agent["id"],)).fetchall()

if rows:
    for r in rows:
        label = "🔻 صرف" if r[1]=="out" else "🔺 توريد"
        color = "red" if r[1]=="out" else "green"
        st.markdown(f"<div style='color:{color};'><strong>{label}</strong> | {r[0]} | {r[2]} ر.س | {r[3]}</div>", unsafe_allow_html=True)
else:
    st.info("لا يوجد سجل بعد." if rtl else "No records yet.")
