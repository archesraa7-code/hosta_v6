# app.py — Hilben Hotel Ops Pro (UI Shell, Clean)
import streamlit as st
from datetime import date
from db import _conn  # ملاحظة: _conn هو اتصال SQLite جاهز (ليس دالة)

# ---------------------- إعداد عام ----------------------
st.set_page_config(
    page_title="Hilben — Hotel Ops Pro",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------- CSS (ثيم + RTL) ----------------------
st.markdown("""
<style>
/* RTL */
html, body, [class*="css"] { direction: rtl; text-align: right; }

/* ألوان */
:root{
  --hilben-blue:#0f1e3a;
  --hilben-blue-2:#182a52;
  --hilben-gold:#D4AF37;
  --card-bg:#0c1428;
}
main, .stApp { background: linear-gradient(180deg, #0b1529 0%, #0a1324 100%); }

/* عناوين */
h1, h2, h3 { color: #fff !important; letter-spacing:.3px; }

/* شريط التابات */
.navbar{
  margin: 4px 0 18px 0; padding: 10px 12px;
  background: var(--hilben-blue);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 12px; display:flex; gap:10px; align-items:center;
}
.navlink{
  padding: 10px 14px; background: var(--hilben-blue-2); color:#fff;
  border: 1px solid rgba(255,255,255,.1); border-radius: 10px;
  text-decoration:none !important; font-weight:600; font-size:14px;
  transition: all .15s;
}
.navlink:hover{ border-color: var(--hilben-gold); color: var(--hilben-gold) !important; }

/* بطاقات */
.card{ background: var(--card-bg); border:1px solid rgba(255,255,255,.06);
  border-radius:14px; padding:16px 18px; color:#e7eaf3; }
.card h4{ margin:0 0 6px 0; color:#cfd7ea; font-weight:700; }
.card .num{ font-size:28px; font-weight:800; color:#fff; }
.gold{ border-color: rgba(212,175,55,.4); box-shadow: 0 0 0 1px rgba(212,175,55,.2) inset; }
.green{ border-color: rgba(84,214,123,.35); }
.red{ border-color: rgba(255,112,112,.35); }
.blue{ border-color: rgba(120,165,255,.35); }

/* أزرار */
.stButton>button{
  background: var(--hilben-gold); color:#1a1a1a; font-weight:700;
  border:0; border-radius:10px; padding:.6rem 1rem;
}
.stButton>button:hover{ filter:brightness(.95); }

/* إخفاء السايدبار */
section[data-testid="stSidebar"]{ display:none !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------- شريط التابات ----------------------
st.markdown("""
<div class="navbar">
  <a class="navlink" href="/">الواجهة الرئيسية</a>
  <a class="navlink" href="/الحجوزات">الحجوزات</a>
  <a class="navlink" href="/كشف_الحساب">كشف الحساب</a>
  <a class="navlink" href="/المصروفات">المصروفات</a>
  <a class="navlink" href="/4_مستحقات_الفنادق">مستحقات الفنادق</a>
  <a class="navlink" href="/5_مستحقات_المطاعم">مستحقات المطاعم</a>
  <a class="navlink" href="/8_السندات">السندات</a>
</div>
""", unsafe_allow_html=True)

# ---------------------- Dashboard ----------------------
st.title("لوحة التحكم — Hotel Ops Pro")

conn = _conn

today = date.today().isoformat()

# عدد الحجوزات الكلي
total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0] or 0

# الحجوزات النشطة اليوم
active_today = conn.execute("""
SELECT COUNT(*) FROM bookings
WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
""", (today, today)).fetchone()[0] or 0

# أرصدة ledger
def ledger_net(party_type):
    row = conn.execute("""
        SELECT COALESCE(SUM(
        CASE WHEN direction='debit' THEN amount
        WHEN direction='credit' THEN -amount
        ELSE 0 END),0)
        FROM ledger WHERE party_type = ?
    """, (party_type,)).fetchone()
    return row[0] if row else 0

due_hotels = ledger_net("hotel")
due_restaurants = ledger_net("restaurant")
due_clients = ledger_net("client")

# عرض البطاقات
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"""<div class="card gold"><h4>إجمالي الحجوزات</h4><div class="num">{total_bookings}</div></div>""", unsafe_allow_html=True)
c2.markdown(f"""<div class="card blue"><h4>نشط اليوم</h4><div class="num">{active_today}</div></div>""", unsafe_allow_html=True)
c3.markdown(f"""<div class="card red"><h4>مستحق للفنادق (ر.س)</h4><div class="num">{due_hotels:,.2f}</div></div>""", unsafe_allow_html=True)
c4.markdown(f"""<div class="card green"><h4>مستحق للمطاعم (ر.س)</h4><div class="num">{due_restaurants:,.2f}</div></div>""", unsafe_allow_html=True)

st.markdown("")

# جدول التشغيل اليومي
st.subheader("تشغيل اليوم")

daily = conn.execute("""
SELECT 
(SELECT name FROM clients WHERE id=bookings.client_id) AS client,
(SELECT name FROM hotels  WHERE id=bookings.hotel_id) AS hotel,
rooms, pax, checkin, checkout
FROM bookings
WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
ORDER BY checkin
""", (today, today)).fetchall()

if daily:
    st.table(daily)
else:
    st.info("لا توجد تشغيلات اليوم ✅")
