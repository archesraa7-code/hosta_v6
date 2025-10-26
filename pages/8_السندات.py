import streamlit as st
from db import _conn, party_balance
from db import add_agent_cash  # نستخدمها للسندات أيضاً
from datetime import datetime

if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"

rtl = (st.session_state["lang"] == "ar")

if rtl:
    st.markdown("""
    <style>
    html, body, [class^='css']{ direction:RTL; text-align:right; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧾 السندات" if rtl else "🧾 Receipts & Vouchers")

conn = _conn()

tab1, tab2 = st.tabs([
    "📥 سند قبض" if rtl else "📥 Receipt",
    "📤 سند صرف" if rtl else "📤 Payment"
])


# --------------------- سند قبض ---------------------
with tab1:
    st.subheader("📥 سند قبض من عميل" if rtl else "Receipt From Client")

    clients = conn.execute("SELECT id,name FROM clients").fetchall()
    client = st.selectbox("اختر العميل" if rtl else "Select Client", clients, format_func=lambda x: x["name"])

    amount = st.number_input("المبلغ (ر.س)" if rtl else "Amount (SAR)", min_value=0.0, step=1.0, format="%.2f")
    note = st.text_input("البيان" if rtl else "Description")

    if st.button("حفظ السند ✅" if rtl else "Save ✅"):
        conn.execute("""
        INSERT INTO ledger(ts, party_type, party_id, ref_type, ref_code, description, debit)
        VALUES (?, 'client', ?, 'receipt', 'RECEIPT', ?, ?)
        """, (datetime.now(), client["id"], note, amount))
        conn.commit()
        st.success("✅ تم تسجيل سند القبض" if rtl else "✅ Receipt Saved")
        st.experimental_rerun()


# --------------------- سند صرف ---------------------
with tab2:
    st.subheader("📤 سند صرف" if rtl else "Payment Voucher")

    party_type = st.selectbox("الجهة" if rtl else "Party Type", [
        "hotel","restaurant","agent"
    ], format_func=lambda x: {"hotel":"فندق","restaurant":"مطعم","agent":"مندوب"}[x] if rtl else x)

    if party_type == "hotel":
        items = conn.execute("SELECT id,name_ar n FROM hotels").fetchall()
    elif party_type == "restaurant":
        items = conn.execute("SELECT id,name_ar n FROM restaurants").fetchall()
    else:
        items = conn.execute("SELECT id,name n FROM agents").fetchall()

    target = st.selectbox("الاسم" if rtl else "Name", items, format_func=lambda x: x["n"])
    amount2 = st.number_input("المبلغ (ر.س)" if rtl else "Amount (SAR)", min_value=0.0, step=1.0, format="%.2f")
    note2 = st.text_input("البيان" if rtl else "Description")

    if st.button("حفظ السند ✅", key="pay_btn"):
        conn.execute("""
        INSERT INTO ledger(ts, party_type, party_id, ref_type, ref_code, description, credit)
        VALUES (?, ?, ?, 'payment', 'PAYMENT', ?, ?)
        """, (datetime.now(), party_type, target["id"], note2, amount2))
        conn.commit()
        st.success("✅ تم تسجيل سند الصرف" if rtl else "✅ Payment Saved")
        st.experimental_rerun()
