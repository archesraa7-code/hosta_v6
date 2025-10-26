import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="كشف الحساب", page_icon="📒", layout="wide")

def get_conn():
    return sqlite3.connect("hotel.db")

st.markdown("<h2 style='text-align:right;'>📒 كشف حساب العميل</h2>", unsafe_allow_html=True)
st.write("---")

# اختيار عميل
conn = get_conn()
customers = conn.execute("SELECT DISTINCT customer FROM reservations").fetchall()
customers = [c[0] for c in customers]
conn.close()

if customers:
    customer = st.selectbox("اختر العميل", customers)
else:
    st.warning("لا يوجد عملاء بعد.")
    st.stop()

# حساب الإجماليات
conn = get_conn()
reservations = conn.execute("SELECT total_cost FROM reservations WHERE customer = ?", (customer,)).fetchall()
payments = conn.execute("SELECT amount FROM payments WHERE customer = ?", (customer,)).fetchall()
conn.close()

total_due = sum([r[0] for r in reservations])
total_paid = sum([p[0] for p in payments])
remaining = total_due - total_paid

col1, col2, col3 = st.columns(3)
col1.metric("إجمالي المستحق", f"{total_due:.2f} ر.س")
col2.metric("المدفوع", f"{total_paid:.2f} ر.س")
col3.metric("المتبقي", f"{remaining:.2f} ر.س")

st.write("---")

# إضافة دفعة
with st.form("add_payment", clear_on_submit=True):
    st.markdown("### 💵 تسجيل دفعة")
    pay_amount = st.number_input("المبلغ", min_value=0.0, step=1.0)
    submit_payment = st.form_submit_button("تسجيل الدفعة ✅")

    if submit_payment:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO payments(customer, amount, date) VALUES (?, ?, ?)", 
                    (customer, pay_amount, str(datetime.now().date())))
        conn.commit()
        conn.close()
        st.success("✅ تم تسجيل الدفعة بنجاح")
        st.experimental_rerun()

# عرض جميع الحركات
st.write("### 🧾 سجل المدفوعات")
conn = get_conn()
history = conn.execute("SELECT amount, date FROM payments WHERE customer = ?", (customer,)).fetchall()
conn.close()

if history:
    for h in history:
        st.write(f"📌 **{h[1]}** — دفع: **{h[0]}** ر.س")
else:
    st.info("لا يوجد مدفوعات لهذا العميل بعد.")
