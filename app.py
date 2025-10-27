# app.py — Hilben Ops Pro (Dashboard Pro: Rooms + Meals)
import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, timedelta

# ================= Page Config & RTL =================
st.set_page_config(page_title="Hilben Ops Pro", page_icon="🏨", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl; text-align: right; }
.stApp { background: linear-gradient(180deg, #0b1529 0%, #0a1324 100%); }
h1,h2,h3,h4 { color:#fff !important; }
.card{ background:#0c1428; border:1px solid rgba(255,255,255,.08);
       border-radius:12px; padding:14px; color:#e7eaf3; }
.card .num{ font-size:24px; font-weight:800; color:#fff; }
.gold{ border-color: rgba(212,175,55,.45); }
.blue{ border-color: rgba(120,165,255,.35); }
.red{  border-color: rgba(255,112,112,.35); }
.green{border-color: rgba(84,214,123,.35); }
.badge{ display:inline-block; margin:4px 6px 0 0; padding:6px 10px; border-radius:10px;
        font-weight:700; font-size:12px; color:#111; }
.b-red{ background:#ffb3b3; } .b-orange{ background:#ffd6a1; }
.b-purple{ background:#d8c8ff; } .b-blue{ background:#cde4ff; }
.stButton>button{ background:#D4AF37; color:#1a1a1a; font-weight:700; border:0; border-radius:10px; padding:.55rem 1rem; }
.stButton>button:hover{ filter:brightness(.92); }
table { direction: rtl !important; text-align:right !important; }
</style>
""", unsafe_allow_html=True)

# ================= Sidebar (Arabic links to English page files) =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>Hilben Ops Pro 🏨</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### إدارة العمليات")
    st.page_link("app.py", label="🏠 الصفحة الرئيسية")
    st.page_link("pages/1_bookings.py", label="🧾 إدارة الحجوزات")
    st.page_link("pages/2_clients.py", label="👥 إدارة العملاء")
    st.page_link("pages/3_hotels.py", label="🏨 إدارة الفنادق")
    st.page_link("pages/4_restaurants.py", label="🍽️ إدارة المطاعم")
    st.page_link("pages/5_employees.py", label="👨‍💼 إدارة الموظفين")
    st.divider()
    st.markdown("### العمليات المالية")
    st.page_link("pages/6_vouchers.py", label="🧾 السندات (قبض / صرف)")
    st.page_link("pages/7_expenses.py", label="💸 المصروفات اليومية")
    st.page_link("pages/8_statements.py", label="📄 كشف الحسابات")
    st.page_link("pages/9_reports.py", label="💰 الأربحية والتقارير")
    st.divider()
    st.page_link("pages/10_settings.py", label="⚙️ إعدادات الشركة")

# ================= DB Connection =================
DB_PATH = "hotel.db"
def get_conn():
    try:
        return sqlite3.connect(DB_PATH, check_same_thread=False)
    except Exception:
        return None

conn = get_conn()
today = date.today()
today_s = today.isoformat()
tomorrow_s = (today + timedelta(days=1)).isoformat()
minus3_s = (today - timedelta(days=3)).isoformat()
minus7_s = (today - timedelta(days=7)).isoformat()

def scalar(q, p=()):
    try:
        r = conn.execute(q, p).fetchone()
        return float(r[0] or 0) if r else 0.0
    except Exception:
        return 0.0

def table(q, p=()):
    try:
        return conn.execute(q, p).fetchall()
    except Exception:
        return []

# Helpers to survive missing tables/columns
def count_rows(tbl):
    try: return int(scalar(f"SELECT COUNT(*) FROM {tbl}"))
    except Exception: return 0

def sum_ledger(party_type=None, by='net'):
    # by='net' -> debit - credit
    try:
        if party_type:
            q = "SELECT direction, amount FROM ledger WHERE party_type=?"
            rows = table(q, (party_type,))
        else:
            rows = table("SELECT direction, amount FROM ledger")
        total = 0.0
        for (d,a) in rows:
            if (d or '').lower() == 'debit':
                total += float(a or 0)
            elif (d or '').lower() == 'credit':
                total -= float(a or 0)
        return total
    except Exception:
        return 0.0

# ================= KPIs Computation =================
total_bookings   = count_rows("bookings")
total_clients    = max(count_rows("clients"), count_rows("customers"))
total_hotels     = count_rows("hotels")
total_restaurants= count_rows("restaurants")

active_today = 0
try:
    active_today = int(scalar("""
        SELECT COUNT(*) FROM bookings
        WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
    """, (today_s, today_s)))
except Exception:
    active_today = 0

# Revenue / Cost / Profit (rooms + meals)
def revenue_today():
    try:
        x = scalar("""
            SELECT COALESCE(SUM(rooms*price_room + pax*price_food),0)
            FROM bookings
            WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
        """, (today_s, today_s))
        return x
    except Exception:
        return 0.0

def cost_today():
    try:
        # if columns missing -> 0
        x = scalar("""
            SELECT COALESCE(SUM(rooms*cost_room + pax*cost_meal),0)
            FROM bookings
            WHERE date(checkin) <= date(?) AND date(checkout) >= date(?)
        """, (today_s, today_s))
        return x
    except Exception:
        return 0.0

rev_today  = revenue_today()
cost_today_v = cost_today()
profit_today = rev_today - cost_today_v

# Ledger nets
due_clients      = sum_ledger("client")       # ما لنا على العملاء (net)
due_hotels_net   = sum_ledger("hotel")        # ما للفنادق علينا (net)
due_rest_net     = sum_ledger("restaurant")   # ما للمطاعم علينا (net)

# Expenses today
expenses_today = 0.0
try:
    expenses_today = scalar("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date(ts)=date(?)", (today_s,))
except Exception:
    expenses_today = 0.0

# ================= Alerts =================
alerts = []

# Check-out today
try:
    co_today = int(scalar("SELECT COUNT(*) FROM bookings WHERE date(checkout)=date(?)", (today_s,)))
    if co_today > 0: alerts.append((f"🟠 {co_today} حجز/حجوزات Check-Out اليوم — راجع التسليم والفواتير.", "b-orange"))
except Exception: pass

# Late departures (past 3 days)
try:
    late_cnt = int(scalar("""
        SELECT COUNT(*) FROM bookings
        WHERE date(checkout) < date(?) AND date(checkout) >= date(?)
    """, (today_s, minus3_s)))
    if late_cnt > 0: alerts.append((f"🔴 {late_cnt} حجز/حجوزات متأخرة عن المغادرة (آخر 3 أيام).", "b-red"))
except Exception: pass

# High balances
if abs(due_clients) >= 5000:      alerts.append(("🟣 مديونية عملاء مرتفعة (≥ 5,000 ر.س).", "b-purple"))
if abs(due_hotels_net) >= 5000:   alerts.append(("🟡 مستحقات فنادق مرتفعة (≥ 5,000 ر.س).", "b-blue"))
if abs(due_rest_net) >= 5000:     alerts.append(("🟡 مستحقات مطاعم مرتفعة (≥ 5,000 ر.س).", "b-blue"))

# ================= Dashboard UI =================
st.markdown("<h1 style='text-align:center; font-weight:800;'>لوحة التحكم الرئيسية</h1>", unsafe_allow_html=True)
st.caption("نظرة شاملة على التشغيل والمحاسبة — الغرف + الوجبات.")

# KPI row 1
k1,k2,k3,k4 = st.columns(4)
k1.markdown(f"<div class='card gold'><h4>إجمالي الحجوزات</h4><div class='num'>{total_bookings}</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='card blue'><h4>الحجوزات النشطة اليوم</h4><div class='num'>{active_today}</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='card blue'><h4>عدد العملاء</h4><div class='num'>{total_clients}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='card blue'><h4>الفنادق / المطاعم</h4><div class='num'>{total_hotels} / {total_restaurants}</div></div>", unsafe_allow_html=True)

# KPI row 2
k5,k6,k7,k8 = st.columns(4)
k5.markdown(f"<div class='card green'><h4>إيراد اليوم</h4><div class='num'>{rev_today:,.2f} ر.س</div></div>", unsafe_allow_html=True)
k6.markdown(f"<div class='card red'><h4>تكلفة اليوم</h4><div class='num'>{cost_today_v:,.2f} ر.س</div></div>", unsafe_allow_html=True)
k7.markdown(f"<div class='card gold'><h4>ربح اليوم (غرف + وجبات)</h4><div class='num'>{profit_today:,.2f} ر.س</div></div>", unsafe_allow_html=True)
k8.markdown(f"<div class='card red'><h4>مصروفات اليوم</h4><div class='num'>{expenses_today:,.2f} ر.س</div></div>", unsafe_allow_html=True)

# Alerts bar
if alerts:
    st.markdown("### تنبيهات")
    html = "".join([f"<span class='badge {klass}'>{txt}</span>" for (txt,klass) in alerts])
    st.markdown(html, unsafe_allow_html=True)

st.markdown("---")

# ============= Quick Tables (Last 10) =============
cA, cB = st.columns(2)

with cA:
    st.markdown("### 📋 آخر 10 حجوزات")
    rows = []
    try:
        rows = table("""
        SELECT
          COALESCE((SELECT name FROM clients WHERE id=b.client_id),
                   (SELECT name FROM customers WHERE id=b.client_id), '—') AS العميل,
          COALESCE((SELECT name FROM hotels WHERE id=b.hotel_id), '—') AS الفندق,
          (b.rooms*b.price_room + b.pax*b.price_food) AS المبلغ,
          b.checkin AS الدخول, b.checkout AS الخروج,
          COALESCE(b.notes,'') AS ملاحظات
        FROM bookings b
        ORDER BY b.id DESC
        LIMIT 10
        """)
    except Exception:
        pass
    df = pd.DataFrame(rows, columns=["العميل","الفندق","المبلغ","الدخول","الخروج","ملاحظات"]) if rows else pd.DataFrame(
        [["—","—","—","—","—","—"]], columns=["العميل","الفندق","المبلغ","الدخول","الخروج","ملاحظات"]
    )
    st.table(df)

with cB:
    st.markdown("### 🧾 آخر 10 سندات (قبض/صرف)")
    vrows = []
    try:
        vrows = table("""
        SELECT ts, party_type, party_id, direction, amount, ref_type, ref_id
        FROM ledger
        ORDER BY ts DESC
        LIMIT 10
        """)
    except Exception:
        pass
    vdf = pd.DataFrame(vrows, columns=["التاريخ","الجهة","رقم الجهة","النوع","المبلغ","مرجع","رقم المرجع"]) if vrows else pd.DataFrame(
        [["—","—","—","—","—","—","—"]], columns=["التاريخ","الجهة","رقم الجهة","النوع","المبلغ","مرجع","رقم المرجع"]
    )
    st.table(vdf)

st.markdown("---")

# ============= Charts (Weekly Revenue & Hotel Mix) =============
st.markdown("### 📈 إيرادات آخر 7 أيام (تجريبي)")
# لو عندك جدول daily_revenue (date, revenue) بنجيب آخر 7 أيام، وإلا نعرض صفار
rev7 = []
try:
    rev7 = table("""
        SELECT strftime('%w', d) AS dow,
               COALESCE(SUM(revenue),0) AS rev
        FROM (
          SELECT date(checkin) AS d,
                 (rooms*price_room + pax*price_food) AS revenue
          FROM bookings
          WHERE date(checkin) >= date(?) AND date(checkin) <= date(?)
        )
        GROUP BY dow
        ORDER BY dow
    """, (minus7_s, today_s))
except Exception:
    rev7 = []

if rev7:
    # dow: 0=الأحد في sqlite عادة؛ نخليها أسماء عربية مرتبة
    names = ["أحد","اثنين","ثلاثاء","أربعاء","خميس","جمعة","سبت"]
    data = pd.DataFrame({
        "اليوم": [names[int(r[0])%7] for r in rev7],
        "الإيراد": [float(r[1] or 0) for r in rev7]
    })
else:
    data = pd.DataFrame({"اليوم":["سبت","أحد","اثنين","ثلاثاء","أربعاء","خميس","جمعة"], "الإيراد":[0,0,0,0,0,0,0]})
st.line_chart(data, x="اليوم", y="الإيراد")

st.markdown("---")
st.caption("© Hilben Ops Pro — Dashboard محسّنة: غرف + وجبات، مع تنبيهات وربحية ومؤشرات وتشارتات. روابط السايدبار مرتبطة بملفات pages/ الإنجليزية.")
