# app.py  — Hilben Hotel Ops Pro (UI Shell)
import streamlit as st
from datetime import date
from db import _conn

# ============== إعداد عام ==============
st.set_page_config(
    page_title="Hilben — Hotel Ops Pro",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============== CSS (ثيم أزرق ملكي + ذهبي + RTL) ==============
st.markdown("""
<style>
/* اتجاه عربي */
html, body, [class*="css"] { direction: rtl; text-align: right; }

/* ألوان عامة */
:root{
  --hilben-blue:#0f1e3a;  /* كحلي */
  --hilben-blue-2:#182a52; 
  --hilben-gold:#D4AF37;  /* ذهبي */
  --card-bg:#0c1428; 
}

/* خلفية */
main, .stApp { background: linear-gradient(180deg, #0b1529 0%, #0a1324 100%); }

/* العنوان الرئيسي */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
  color: white !important;
  letter-spacing: .3px;
}

/* شريط التابات العلوي */
.navbar{
  margin: 4px 0 18px 0;
  padding: 10px 12px;
  background: var(--hilben-blue);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  display:flex;
  gap:10px;
  justify-content:flex-start;
  align-items:center;
}
.navlink{
  padding: 10px 14px;
  background: var(--hilben-blue-2);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  text-decoration:none !important;
  font-weight:600;
  font-size: 14px;
  transition: all .15s;
}
.navlink:hover{ border-color: var(--hilben-gold); color: var(--hilben-gold) !important; }

/* بطاقات الإحصائيات */
.card{
  background: var(--card-bg);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 14px;
  padding: 16px 18px;
  color: #e7eaf3;
}
.card h4{ margin:0 0 6px 0; color:#cfd7ea; font-weight:700; }
.card .num{ font-size:28px; font-weight:800; color:#fff; }
.gold{ border-color: rgba(212,175,55,.4); box-shadow: 0 0 0 1px rgba(212,175,55,.2) inset; }
.green{ border-color: rgba(84,214,123,.35); }
.red{ border-color: rgba(255,112,112,.35); }
.blue{ border-color: rgba(120,165,255,.35); }

/* جداول */
[data-testid="stTable"] table, .stDataFrame{ direction: rtl !important; }

/* أزرار */
.stButton>button{
  background: var(--hilben-gold); color:#1a1a1a; font-weight:700;
  border:0; border-radius:10px; padding:.6rem 1rem;
}
.stButton>button:hover{ filter:brightness(.95); }

/* إخفاء السايدبار */
.css-163ttbj, section[data-testid="stSidebar"]{ display:none !important; }
</style>
""", unsafe_allow_html=True)

# ============== شريط التابات (روابط الصفحات) ==============
st.markdown(
    """
    <div class="navbar">
      <a class="navlink" href="/">الواجهة الرئيسية</a>
      <a class="navlink" href="/الحجوزات">الحجوزات</a>
      <a class="navlink" href="/كشف_الحساب">كشف الحساب</a>
      <a class="navlink" href="/المصروفات">المصروفات</a>
      <a class="navlink" href="/4_مستحقات_الفنادق">مستحقات الفنادق</a>
      <a class="navlink" href="/5_مستحقات_المطاعم">مستحقات المطاعم</a>
      <a class="navlink" href="/8_السندات">السندات</a>
    </div>
    """,
    unsafe_allow_html=True
)

# ============== Dashboard ==============
st.title("لوحة التحكم — Hotel Ops Pro")

conn = _conn()

# احصائيات أساسية
today = date.today().isoformat()

# عدد الحجوزات النشطة اليوم (متقاطعة مع اليوم)
q_active = """
SELECT COUNT(*) 
FROM bookings 
WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
"""
active_today = conn.execute(q_active, (today, today)).fetchone()[0] or 0

total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0] or 0

# أرصدة من دفتر الأستاذ بحسب النوع (مدين - دائن)
def signed_sum(party_type: str) -> float:
    q = """
    SELECT COALESCE(SUM(CASE WHEN direction='debit' THEN amount ELSE -amount END), 0)
    FROM ledger WHERE party_type = ?
    """
    return float(conn.execute(q, (party_type,)).fetchone()[0] or 0)

due_hotels = signed_sum("hotel")         # ما يستحق للفنادق (+)
due_restaurants = signed_sum("restaurant")
receivable_clients = signed_sum("client")  # ما على العملاء (+)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="card gold">
      <h4>إجمالي الحجوزات</h4>
      <div class="num">{total_bookings}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="card blue">
      <h4>حجوزات نشطة اليوم</h4>
      <div class="num">{active_today}</div>
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
      • من شريط التابات العلوي انتقل لأي صفحة مباشرة. <br/>
      • في صفحة الحجوزات، الحساب يتم تلقائياً (أيام × غرف × أسعار + الوجبات). <br/>
      • عند حفظ الحجز: يُسجل قيد في دفتر الأستاذ تلقائياً. <br/>
      • كشف الحساب يعتمد على الـ Ledger ويعرض الرصيد فوراً.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© Hilben — Hotel Ops Pro v4 • واجهة احترافية وثيم أزرق ملكي + ذهبي • RTL كامل")
