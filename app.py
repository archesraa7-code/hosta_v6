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

conn = _conn  # اتصال جاهز (لا تضف أقواس)

def fetch_scalar(sql: str, params: tuple = ()) -> float:
    """إرجاع قيمة رقمية بأمان (0 لو مفيش نتيجة أو الجدول غير موجود)."""
    try:
        row = conn.execute(sql, params).fetchone()
        if not row: 
            return 0
        val = row[0]
        return float(val) if val is not None else 0.0
    except Exception:
        return 0.0

today = date.today().isoformat()

# إجمالي الحجوزات
total_bookings = fetch_scalar("SELECT COUNT(*) FROM bookings")

# الحجوزات النشطة اليوم
q_active = """
SELECT COUNT(*)
FROM bookings
WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
"""
active_today = fetch_scalar(q_active, (today, today))

# أرصدة من دفتر الأستاذ حسب النوع (debit + / credit -)
def ledger_net(party_type: str) -> float:
    sql = """
    SELECT COALESCE(SUM(CASE WHEN direction='debit' THEN amount
                             WHEN direction='credit' THEN -amount
                             ELSE 0 END), 0)
    FROM ledger
    WHERE party_type = ?
    """
    return fetch_scalar(sql, (party_type,))

due_hotels       = ledger_net("hotel")        # لصالح الفنادق +
due_restaurants  = ledger_net("restaurant")   # لصالح المطاعم +
receivable_clients = ledger_net("client")     # على العملاء +

# عرض البطاقات
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="card gold">
      <h4>إجمالي الحجوزات</h4>
      <div class="num">{int(total_bookings)}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="card blue">
      <h4>حجوزات نشطة اليوم</h4>
      <div class="num">{int(active_today)}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="card red">
      <h4>مستحقات الفنادق (ر.س)</h4>
      <div class="num">{due_hotels:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="card green">
      <h4>مستحقات المطاعم (ر.س)</h4>
      <div class="num">{due_restaurants:,.2f}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")
c5, c6 = st.columns(2)
with c5:
    st.markdown(f"""
    <div class="card">
      <h4>المطلوب من العملاء (ر.س)</h4>
      <div class="num">{receivable_clients:,.2f}</div>
    </div>""", unsafe_allow_html=True)

with c6:
    st.markdown("""
    <div class="card">
      <h4>نصائح سريعة</h4>
      • انتقل بين الصفحات من الشريط العلوي. <br/>
      • صفحة الحجوزات بحساب تلقائي (أيام × غرف + الوجبات). <br/>
      • القيود تُسجّل في دفتر الأستاذ لعرض كشف الحساب فورًا. <br/>
      • الثيم أزرق ملكي + ذهبي، واتجاه عربي كامل.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© Hilben — Hotel Ops Pro v4 • ثيم أزرق ملكي + ذهبي • RTL كامل")
