# app.py — Hilben Hotel Ops Pro (Final Dashboard, No Fixed Hotel Capacity)
import streamlit as st
from datetime import date, timedelta
from db import _conn  # اتصال SQLite جاهز (بدون أقواس)

# -------------------------------------------------------------
# إعداد الصفحة
# -------------------------------------------------------------
st.set_page_config(
    page_title="Hilben — Hotel Ops Pro",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

conn = _conn
today = date.today()
today_s = today.isoformat()
in_3_days = (today + timedelta(days=3)).isoformat()

# -------------------------------------------------------------
# الثيم + RTL
# -------------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl; text-align: right; }
.stApp { background: linear-gradient(180deg, #0b1529 0%, #0a1324 100%); }

/* عناوين */
h1, h2, h3 { color: #fff !important; }

/* بطاقات */
.card{
  background:#0c1428; border-radius:14px; padding:14px 16px;
  border:1px solid rgba(255,255,255,.06); color:#e7eaf3;
}
.card .num{ font-size:24px; font-weight:800; }

/* ألوان بطاقات */
.gold{ border-color: rgba(212,175,55,.45); }
.blue{ border-color: rgba(120,165,255,.35); }
.red{ border-color: rgba(255,112,112,.35); }
.green{ border-color: rgba(84,214,123,.35); }

/* أزرار */
.stButton>button{
  background:#D4AF37; color:#1a1a1a; border-radius:8px;
  padding:6px 18px; font-weight:700; border:0;
}
.stButton>button:hover{ filter:brightness(.92); }

/* جداول */
table { direction: rtl !important; text-align:right !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR — الأقسام
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🟢 العمليات اليومية")
    st.page_link("pages/1_الحجوزات.py", label="إدارة الحجوزات", icon="📝")
    st.page_link("pages/2_العمليات_اليومية.py", label="Check-in / Check-out اليوم", icon="🔄")

    st.markdown("## 🟣 إدارة البيانات")
    st.page_link("pages/3_العملاء.py", label="العملاء", icon="👥")
    st.page_link("pages/4_الفنادق.py", label="الفنادق", icon="🏨")
    st.page_link("pages/5_المطاعم.py", label="المطاعم", icon="🍽️")
    st.page_link("pages/6_الموظفين.py", label="الموظفين", icon="🧑‍💼")

    st.markdown("## 🟡 الحسابات")
    st.page_link("pages/7_كشف_الحساب.py", label="كشف حساب العملاء", icon="📄")
    st.page_link("pages/8_مستحقات_الفنادق.py", label="مستحقات الفنادق", icon="🏨")
    st.page_link("pages/9_مستحقات_المطاعم.py", label="مستحقات المطاعم", icon="🍛")
    st.page_link("pages/10_المصروفات.py", label="المصروفات اليومية", icon="💸")
    st.page_link("pages/11_عهدة_المندوب.py", label="عهدة المندوب", icon="🧾")

    st.markdown("## 🔴 الفواتير والسندات والتقارير")
    st.page_link("pages/12_الفواتير.py", label="الفواتير", icon="🧾")
    st.page_link("pages/13_السندات.py", label="سندات قبض / صرف", icon="📝")
    st.page_link("pages/14_التقارير.py", label="التقارير الإحصائية", icon="📊")

    st.markdown("---")
    st.caption("Hilben Hotel Ops Pro — النسخة التجارية")

# -------------------------------------------------------------
# دوال مساعدة
# -------------------------------------------------------------
def fetch_scalar(sql: str, params: tuple = ()) -> float:
    try:
        row = conn.execute(sql, params).fetchone()
        if not row: return 0
        return float(row[0] or 0)
    except Exception:
        return 0.0

def try_clients_or_customers_base(select_cols: str, where_sql: str, params: tuple):
    """
    يحاول يعرض اسم العميل من جدول clients؛ لو غير موجود يستخدم customers.
    select_cols: نص الأعمدة بعد SELECT (مثلاً 'c.name AS العميل, ...')
    where_sql: جزء WHERE .../ ORDER BY...
    """
    # محاولة بجدول clients
    sql_clients = f"""
    SELECT 
      (SELECT name FROM clients WHERE id=b.client_id) AS العميل,
      (SELECT name FROM hotels  WHERE id=b.hotel_id)  AS الفندق,
      b.rooms AS الغرف, b.pax AS الافراد, b.checkin AS دخول, b.checkout AS خروج
    FROM bookings b
    {where_sql}
    """
    try:
        return conn.execute(sql_clients, params).fetchall()
    except Exception:
        # محاولة بجدول customers
        sql_customers = f"""
        SELECT 
          (SELECT name FROM customers WHERE id=b.client_id) AS العميل,
          (SELECT name FROM hotels  WHERE id=b.hotel_id)    AS الفندق,
          b.rooms AS الغرف, b.pax AS الافراد, b.checkin AS دخول, b.checkout AS خروج
        FROM bookings b
        {where_sql}
        """
        return conn.execute(sql_customers, params).fetchall()

# -------------------------------------------------------------
# KPIs — المؤشرات الرئيسية
# -------------------------------------------------------------
st.title("لوحة التحكم الرئيسية")

total_bookings = fetch_scalar("SELECT COUNT(*) FROM bookings")
active_today   = fetch_scalar("""
    SELECT COUNT(*) FROM bookings
    WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
""", (today_s, today_s))

def ledger_net(party_type: str) -> float:
    return fetch_scalar("""
        SELECT COALESCE(SUM(
          CASE WHEN direction='debit' THEN amount
               WHEN direction='credit' THEN -amount
               ELSE 0 END), 0)
        FROM ledger WHERE party_type=?
    """, (party_type,))

due_hotels      = ledger_net("hotel")
due_restaurants = ledger_net("restaurant")
due_clients     = ledger_net("client")

c1,c2,c3,c4 = st.columns(4)
c1.markdown(f"<div class='card gold'><h4>إجمالي الحجوزات</h4><div class='num'>{int(total_bookings)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card blue'><h4>نشطة اليوم</h4><div class='num'>{int(active_today)}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card red'><h4>مستحق للفنادق (ر.س)</h4><div class='num'>{due_hotels:,.2f}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card green'><h4>مستحق للمطاعم (ر.س)</h4><div class='num'>{due_restaurants:,.2f}</div></div>", unsafe_allow_html=True)

st.markdown("")

# -------------------------------------------------------------
# تشغيل اليوم — الحجوزات النشطة الآن
# -------------------------------------------------------------
st.subheader("تشغيل اليوم — حجوزات نشطة")
active_rows = try_clients_or_customers_base(
    select_cols="",
    where_sql="WHERE date(b.checkin) <= date(?) AND date(b.checkout) >= date(?) ORDER BY b.checkin",
    params=(today_s, today_s)
)
st.table(active_rows) if active_rows else st.info("لا توجد تشغيلات اليوم ✅")

# -------------------------------------------------------------
# حالات اليوم التفصيلية (Check-in / Check-out / متأخرين)
# -------------------------------------------------------------
st.subheader("تفاصيل الواقع التشغيلي")
colA, colB, colC = st.columns(3)

# Check-in اليوم
ci_rows = try_clients_or_customers_base(
    "", "WHERE date(b.checkin)=date(?) ORDER BY b.checkin", (today_s,)
)
with colA:
    st.write("🟢 Check-in اليوم")
    st.table(ci_rows) if ci_rows else st.info("لا يوجد")

# Check-out اليوم
co_rows = try_clients_or_customers_base(
    "", "WHERE date(b.checkout)=date(?) ORDER BY b.checkout", (today_s,)
)
with colB:
    st.write("🟠 Check-out اليوم")
    st.table(co_rows) if co_rows else st.info("لا يوجد")

# متأخرين عن المغادرة (آخر 3 أيام فقط لتكون عملية)
late_rows = try_clients_or_customers_base(
    "", "WHERE date(b.checkout) < date(?) AND date(b.checkout) >= date(?) ORDER BY b.checkout DESC",
    (today_s, (today - timedelta(days=3)).isoformat())
)
with colC:
    st.write("🔴 متأخرين عن المغادرة")
    st.table(late_rows) if late_rows else st.success("لا يوجد تأخير ✅")

st.markdown("")

# -------------------------------------------------------------
# تشغيل الفنادق اليوم (بدون حاجة لسعة الفندق)
# غرف اليوم = rooms × سعر الغرفة لليوم للحجوزات النشطة
# -------------------------------------------------------------
st.subheader("تشغيل الفنادق اليوم")
hotels_today = conn.execute("""
SELECT h.name AS الفندق,
       SUM(b.rooms) AS الغرف_المشغولة_اليوم,
       SUM(b.rooms * b.price_room) AS قيمة_الغرف_اليوم
FROM bookings b
JOIN hotels h ON h.id = b.hotel_id
WHERE date(b.checkin) <= date(?) AND date(b.checkout) >= date(?)
GROUP BY h.name
ORDER BY قيمة_الغرف_اليوم DESC
""", (today_s, today_s)).fetchall()

st.table(hotels_today) if hotels_today else st.info("لا توجد حجوزات نشطة في الفنادق اليوم")

# -------------------------------------------------------------
# تشغيل المطاعم اليوم
# وجبات اليوم = pax × سعر الوجبة لليوم للحجوزات النشطة (فقط لو restaurant_id موجود)
# -------------------------------------------------------------
st.subheader("تشغيل المطاعم اليوم")
restaurants_today = conn.execute("""
SELECT r.name AS المطعم,
       SUM(b.pax) AS الافراد_اليوم,
       SUM(b.pax * b.price_food) AS قيمة_الوجبات_اليوم
FROM bookings b
JOIN restaurants r ON r.id = b.restaurant_id
WHERE b.restaurant_id IS NOT NULL
  AND date(b.checkin) <= date(?) AND date(b.checkout) >= date(?)
GROUP BY r.name
ORDER BY قيمة_الوجبات_اليوم DESC
""", (today_s, today_s)).fetchall()

st.table(restaurants_today) if restaurants_today else st.info("لا توجد تشغيلات مطاعم اليوم")

st.markdown("")

# -------------------------------------------------------------
# حجوزات قادمة خلال 3 أيام + حجوزات ستغادر خلال 3 أيام
# -------------------------------------------------------------
st.subheader("نظرة مستقبلية (3 أيام)")
colF, colG = st.columns(2)

incoming = try_clients_or_customers_base(
    "", "WHERE date(b.checkin) > date(?) AND date(b.checkin) <= date(?) ORDER BY b.checkin",
    (today_s, in_3_days)
)
with colF:
    st.write("🟡 حجوزات قادمة خلال 3 أيام")
    st.table(incoming) if incoming else st.info("لا يوجد حجوزات قادمة قريبة")

leaving_soon = try_clients_or_customers_base(
    "", "WHERE date(b.checkout) >= date(?) AND date(b.checkout) <= date(?) ORDER BY b.checkout",
    (today_s, in_3_days)
)
with colG:
    st.write("🟠 حجوزات ستغادر خلال 3 أيام")
    st.table(leaving_soon) if leaving_soon else st.info("لا يوجد مغادرة قريبة")

st.markdown("---")
st.caption("© Hilben — Hotel Ops Pro | Dashboard تشغيلية ومالية — بدون الحاجة لسعة غرف الفنادق")
