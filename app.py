# app.py — Hilben Hotel Ops Pro (Dashboard + Sidebar)
import streamlit as st
from datetime import date, timedelta
import sqlite3

# ========= إعداد الصفحة =========
st.set_page_config(
    page_title="Hilben — لوحة التحكم",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========= اتصال قاعدة البيانات (عدّل الاسم لو مختلف) =========
DB_PATH = "hotel.db"
def get_conn():
    try:
        return sqlite3.connect(DB_PATH, check_same_thread=False)
    except Exception:
        return None

conn = get_conn()

# ========= ثيم ملكي + RTL =========
st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl; text-align: right; }
.stApp { background: linear-gradient(180deg, #0b1529 0%, #0a1324 100%); }
h1, h2, h3 { color:#fff !important; }

.card{
  background:#0c1428; border:1px solid rgba(255,255,255,.08);
  border-radius:12px; padding:14px; color:#e7eaf3;
}
.card .num{ font-size:24px; font-weight:800; color:#fff; }
.gold{ border-color: rgba(212,175,55,.45); }
.blue{ border-color: rgba(120,165,255,.35); }
.red{  border-color: rgba(255,112,112,.35); }
.green{border-color: rgba(84,214,123,.35); }

.stButton>button{
  background:#D4AF37; color:#1a1a1a; font-weight:700;
  border:0; border-radius:10px; padding:.6rem 1rem;
}
.stButton>button:hover{ filter:brightness(.92); }
table { direction: rtl !important; text-align:right !important; }
.badge{ display:inline-block; margin:4px 6px 0 0; padding:6px 10px; border-radius:10px; font-weight:700; font-size:12px; color:#111; }
.b-red{ background:#ffb3b3; }
.b-orange{ background:#ffd6a1; }
.b-purple{ background:#d8c8ff; }
.b-blue{ background:#cde4ff; }
</style>
""", unsafe_allow_html=True)

# ========= Sidebar (الأقسام) =========
import streamlit as st

st.set_page_config(page_title="Hilben Ops Pro", page_icon="🏨", layout="wide")

# ================= Sidebar Navigation ================
with st.sidebar:
    st.title("🏨 Hilben Ops Pro")
    st.markdown("---")

    st.page_link("app.py", label="🏠 الصفحة الرئيسية")

    st.markdown("### 🧭 إدارة العمليات")
    st.page_link("pages/1_bookings.py", label="🛏️ إدارة الحجوزات")
    st.page_link("pages/2_clients.py", label="👥 إدارة العملاء")
    st.page_link("pages/3_hotels.py", label="🏨 إدارة الفنادق")
    st.page_link("pages/4_restaurants.py", label="🍽️ إدارة المطاعم")
    st.page_link("pages/5_employees.py", label="🧑‍💼 إدارة الموظفين")

    st.markdown("### 💰 العمليات المالية")
    st.page_link("pages/6_vouchers.py", label="🧾 السندات (قبض / صرف)")
    st.page_link("pages/7_expenses.py", label="💸 المصروفات اليومية")
    st.page_link("pages/8_statements.py", label="📄 كشف الحسابات")
    st.page_link("pages/9_reports.py", label="💰 الربحية والتقارير")

    st.markdown("### ⚙️ إعدادات")
    st.page_link("pages/10_settings.py", label="⚙️ إعدادات الشركة")

# ================= Dashboard Content ================
st.title("🏨 لوحة التحكم الرئيسية - Hilben Ops Pro")
st.info("اختر وظيفة من القائمة الجانبية للبدء ✅")
# ========= Helpers =========
def fetch_scalar(sql, params=()):
    try:
        row = conn.execute(sql, params).fetchone()
        return float(row[0] or 0) if row else 0.0
    except Exception:
        return 0.0

def try_clients_or_customers(where_sql, params=()):
    # يحاول clients ثم customers لاسم العميل
    q1 = f"""
    SELECT (SELECT name FROM clients WHERE id=b.client_id) AS العميل,
           (SELECT name FROM hotels  WHERE id=b.hotel_id)  AS الفندق,
           b.rooms AS الغرف, b.pax AS الافراد, b.checkin AS دخول, b.checkout AS خروج
    FROM bookings b {where_sql}
    """
    try:
        return conn.execute(q1, params).fetchall()
    except Exception:
        q2 = f"""
        SELECT (SELECT name FROM customers WHERE id=b.client_id) AS العميل,
               (SELECT name FROM hotels  WHERE id=b.hotel_id)  AS الفندق,
               b.rooms AS الغرف, b.pax AS الافراد, b.checkin AS دخول, b.checkout AS خروج
        FROM bookings b {where_sql}
        """
        return conn.execute(q2, params).fetchall()

# ========= Dashboard =========
st.markdown("<h1 style='text-align:center;font-weight:800;'>📊 لوحة التحكم الرئيسية</h1>", unsafe_allow_html=True)

today = date.today()
today_s = today.isoformat()

# KPIs
total_bookings = fetch_scalar("SELECT COUNT(*) FROM bookings")
active_today   = fetch_scalar("""
    SELECT COUNT(*) FROM bookings
    WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
""", (today_s, today_s))

def ledger_net(party_type):
    return fetch_scalar("""
        SELECT COALESCE(SUM(
            CASE WHEN direction='debit' THEN amount
                 WHEN direction='credit' THEN -amount ELSE 0 END
        ),0) FROM ledger WHERE party_type=?
    """, (party_type,))

due_hotels      = ledger_net("hotel")
due_restaurants = ledger_net("restaurant")
due_clients     = ledger_net("client")

c1,c2,c3,c4 = st.columns(4)
c1.markdown(f"<div class='card gold'><h4>إجمالي الحجوزات</h4><div class='num'>{int(total_bookings)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card blue'><h4>نشطة اليوم</h4><div class='num'>{int(active_today)}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card red'><h4>مستحق للفنادق (ر.س)</h4><div class='num'>{due_hotels:,.2f}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card green'><h4>مستحق للمطاعم (ر.س)</h4><div class='num'>{due_restaurants:,.2f}</div></div>", unsafe_allow_html=True)

# تشغيل اليوم
st.subheader("تشغيل اليوم — حجوزات نشطة")
active_rows = try_clients_or_customers(
    "WHERE date(b.checkin) <= date(?) AND date(b.checkout) >= date(?) ORDER BY b.checkin",
    (today_s, today_s)
)
st.table(active_rows) if active_rows else st.info("لا توجد تشغيلات اليوم ✅")

# تفاصيل اليوم
st.subheader("تفاصيل الواقع التشغيلي")
colA, colB, colC = st.columns(3)

ci = try_clients_or_customers("WHERE date(b.checkin)=date(?) ORDER BY b.checkin", (today_s,))
with colA:
    st.write("🟢 Check-in اليوم")
    st.table(ci) if ci else st.info("لا يوجد")

co = try_clients_or_customers("WHERE date(b.checkout)=date(?) ORDER BY b.checkout", (today_s,))
with colB:
    st.write("🟠 Check-out اليوم")
    st.table(co) if co else st.info("لا يوجد")

late = try_clients_or_customers(
    "WHERE date(b.checkout) < date(?) AND date(b.checkout) >= date(?) ORDER BY b.checkout DESC",
    (today_s, (today - timedelta(days=3)).isoformat())
)
with colC:
    st.write("🔴 متأخرين عن المغادرة")
    st.table(late) if late else st.success("لا يوجد تأخير ✅")

st.markdown("---")
st.caption("© Hilben — Hotel Ops Pro | Dashboard جاهزة + صفحات فارغة للتعبئة اللاحقة")
