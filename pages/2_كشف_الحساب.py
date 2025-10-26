import streamlit as st
from db import _conn, party_balance, party_ledger

if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"

rtl = (st.session_state["lang"] == "ar")

if rtl:
    st.markdown("""
    <style>
    html, body, [class^='css']{ direction: RTL; text-align:right; }
    </style>
    """, unsafe_allow_html=True)

st.title("📒 كشف حساب" if rtl else "📒 Statement")

conn = _conn()

ptype = st.selectbox(
    "اختر الطرف" if rtl else "Select Party",
    ["client","hotel","restaurant","agent"],
    format_func=lambda x: {
        "client":"عميل",
        "hotel":"فندق",
        "restaurant":"مطعم",
        "agent":"مندوب"
    }[x] if rtl else x
)

# تحميل قائمة الأسماء حسب الاختيار
if ptype == "client":
    items = conn.execute("SELECT id,name n FROM clients").fetchall()
elif ptype == "hotel":
    items = conn.execute("SELECT id,name_ar n FROM hotels").fetchall()
elif ptype == "restaurant":
    items = conn.execute("SELECT id,name_ar n FROM restaurants").fetchall()
else:
    items = conn.execute("SELECT id,name n FROM agents").fetchall()

selected = st.selectbox("الاسم" if rtl else "Name", items, format_func=lambda r: r["n"])

if selected:
    balance = party_balance(ptype, selected["id"])
    st.subheader(("الرصيد الحالي: " if rtl else "Balance: ") + f"{balance:,.2f} ر.س")

    data = party_ledger(ptype, selected["id"])

    st.write("**مدين** = علينا له / **دائن** = له علينا" if rtl else "**Debit** / **Credit** Interpretation")

    st.table([
        {
            ("التاريخ" if rtl else "Date"): d,
            ("نوع" if rtl else "Type"): t,
            ("مرجع" if rtl else "Ref"): ref,
            ("البيان" if rtl else "Description"): desc,
            ("مدين" if rtl else "Debit"): f"{debit:,.2f}" if debit else "",
            ("دائن" if rtl else "Credit"): f"{credit:,.2f}" if credit else "",
            ("الرصيد" if rtl else "Balance"): f"{bal:,.2f}"
        }
        for (d,t,ref,desc,debit,credit,bal) in data
    ])
