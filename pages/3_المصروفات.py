import streamlit as st
from db import _conn, add_expense, add_agent_cash, party_balance

if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"

rtl = (st.session_state["lang"] == "ar")

if rtl:
    st.markdown("""
    <style>
    html, body, [class^='css']{ direction:RTL; text-align:right; }
    </style>
    """, unsafe_allow_html=True)

st.title("💸 المصروفات و العهدة" if rtl else "💸 Expenses & Agent Cash")

tab1, tab2 = st.tabs([
    "🧾 مصروف تشغيل" if rtl else "🧾 Expense",
    "👤 عهدة مندوب" if rtl else "👤 Agent Cash"
])

# ------------------------- مصروف تشغيل -------------------------
with tab1:
    st.subheader("تسجيل مصروف" if rtl else "Record Expense")

    amount = st.number_input("المبلغ (ر.س)" if rtl else "Amount (SAR)", min_value=0.0, step=1.0, format="%.2f")
    who = st.text_input("لمن؟" if rtl else "To / For")
    method = st.selectbox(
        "طريقة الدفع" if rtl else "Payment Method",
        ["cash","bank","agent"],
        format_func=lambda x: {"cash":"نقدًا","bank":"تحويل بنكي","agent":"عهدة مندوب"}[x] if rtl else x
    )
    notes = st.text_area("ملاحظات" if rtl else "Notes")

    if st.button("حفظ المصروف ✅" if rtl else "Save ✅"):
        add_expense(amount, who, method, notes)
        st.success("✅ تم تسجيل المصروف" if rtl else "✅ Saved!")

# ------------------------- عهدة مندوب -------------------------
with tab2:
    st.subheader("تسجيل عهدة أو توريد" if rtl else "Agent Cash Movement")

    conn = _conn()
    agents = conn.execute("SELECT id,name FROM agents").fetchall()
    conn.close()

    agent = st.selectbox("المندوب" if rtl else "Agent", agents, format_func=lambda x: x["name"])

    direction = st.radio(
        "نوع العملية" if rtl else "Type",
        ["out","in"],
        format_func=lambda x: {"out":"صرف للمندوب","in":"توريد من المندوب"}[x] if rtl else x,
        horizontal=True
    )

    amount2 = st.number_input("المبلغ" if rtl else "Amount", min_value=0.0, step=1.0, format="%.2f")
    note2 = st.text_input("البيان" if rtl else "Note")

    if st.button("تسجيل العملية ✅" if rtl else "Save ✅"):
        add_agent_cash(agent["id"], amount2, direction, note2)
        st.success("✅ تم تسجيل العملية" if rtl else "✅ Saved!")

    st.write("---")
    st.subheader("رصيد المندوب الحالي" if rtl else "Current Agent Balance")
    st.info(f"{party_balance('agent', agent['id']):,.2f} ر.س")
