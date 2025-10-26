
import streamlit as st
import pandas as pd
from sqlalchemy import select
from datetime import date
import json, os

from db import init_db, Setting, User, Hotel, Restaurant, MealTier, Customer, Booking, Voucher, SessionLocal
from utils_pdf import make_invoice_pdf, make_voucher_pdf

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
LOGO = os.path.join(ASSETS, "logo.png")
EXPORTS = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(EXPORTS, exist_ok=True)

st.set_page_config(page_title="Hotel Ops Pro v4", layout="wide")
session = init_db()

def get_setting(key, default=""):
    s = session.query(Setting).filter(Setting.key==key).first()
    return s.value if s else default

def set_setting(key, value):
    s = session.query(Setting).filter(Setting.key==key).first()
    if not s:
        s = Setting(key=key, value=str(value))
        session.add(s)
    else:
        s.value = str(value)
    session.commit()

if "LANG" not in st.session_state:
    st.session_state["LANG"] = get_setting("LANG","AR")

col1, col2 = st.columns([6,1])
with col1:
    st.title("شركة هيلبن لخدمات المعتمرين — Hotel Ops Pro v4")
with col2:
    if st.button("English" if st.session_state["LANG"]=="AR" else "العربية"):
        st.session_state["LANG"] = "EN" if st.session_state["LANG"]=="AR" else "AR"
        set_setting("LANG", st.session_state["LANG"])
        st.experimental_rerun()

tabs = st.tabs(["لوحة التحكم","إدارة الفنادق","إدارة المطاعم","إدارة العملاء","الحجوزات","إضافة حجز","التقارير","السندات"])

with tabs[1]:
    st.subheader("الفنادق")
    hotels = session.query(Hotel).order_by(Hotel.name).all()
    st.table(pd.DataFrame([{"ID":h.id,"الفندق":h.name} for h in hotels]))
    st.divider()
    name = st.text_input("اسم فندق جديد")
    if st.button("إضافة فندق ✅"):
        if name.strip() and not session.query(Hotel).filter(Hotel.name==name.strip()).first():
            session.add(Hotel(name=name.strip())); session.commit(); st.success("تم"); st.experimental_rerun()

with tabs[2]:
    st.subheader("المطاعم")
    rests = session.query(Restaurant).order_by(Restaurant.name).all()
    st.table(pd.DataFrame([{"ID":r.id,"مطعم":r.name} for r in rests]))
    rname = st.text_input("اسم مطعم جديد")
    if st.button("إضافة مطعم ✅"):
        if rname.strip() and not session.query(Restaurant).filter(Restaurant.name==rname.strip()).first():
            session.add(Restaurant(name=rname.strip())); session.commit(); st.success("تم"); st.experimental_rerun()
    st.divider()
    st.subheader("فئات التسعير (سعر اليوم = ٣ وجبات/شخص)")
    rsel = st.selectbox("مطعم", rests, format_func=lambda x: x.name if x else "")
    if rsel:
        tiers = session.query(MealTier).filter(MealTier.restaurant_id==rsel.id).all()
        st.table(pd.DataFrame([{"ID":t.id,"الفئة":t.name,"سعر اليوم":t.daily_price} for t in tiers]))
        tname = st.text_input("اسم الفئة (مثلاً: بالغ)")
        tprice = st.number_input("السعر/اليوم (٣ وجبات)", min_value=0.0, step=1.0)
        if st.button("حفظ فئة ✅"):
            if tname.strip():
                session.add(MealTier(restaurant_id=rsel.id, name=tname.strip(), daily_price=tprice)); session.commit(); st.success("تم"); st.experimental_rerun()

with tabs[3]:
    st.subheader("العملاء")
    customers = session.query(Customer).order_by(Customer.name).all()
    st.table(pd.DataFrame([{"ID":c.id,"العميل":c.name,"الشركة":c.company or "","المندوب":c.agent or ""} for c in customers]))
    cname = st.text_input("اسم العميل")
    ccomp = st.text_input("اسم الشركة (اختياري)")
    cagent = st.text_input("اسم المندوب (اختياري)")
    if st.button("إضافة عميل ✅"):
        if cname.strip():
            session.add(Customer(name=cname.strip(), company=ccomp.strip() or None, agent=cagent.strip() or None)); session.commit(); st.success("تم"); st.experimental_rerun()

with tabs[4]:
    st.subheader("قائمة الحجوزات")
    qs = session.query(Booking).order_by(Booking.id.desc()).all()
    df = pd.DataFrame([{
        "ID": b.id,
        "حجز": b.booking_no or b.id,
        "فندق": b.hotel.name if b.hotel else "",
        "عميل": b.customer.name if b.customer else "",
        "مطعم": b.restaurant.name if b.restaurant else "",
        "دخول": b.check_in,
        "خروج": b.check_out,
        "ليالي": b.nights,
        "غرف": b.rooms,
        "إجمالي غرف": b.rooms_total,
        "إجمالي وجبات": b.meals_total,
        "الإجمالي": b.total,
        "مدفوع": b.paid,
        "متبقي": b.balance,
        "أرقام الغرف": b.rooms_numbers or ""
    } for b in qs])
    st.dataframe(df, use_container_width=True)

    if st.button("📤 تصدير الحجوزات إلى Excel"):
        xlsx_path = os.path.join(EXPORTS, "bookings.xlsx")
        df.to_excel(xlsx_path, index=False)
        st.success(f"تم إنشاء الملف: {xlsx_path}")

with tabs[5]:
    st.subheader("إضافة حجز")
    hotels = session.query(Hotel).order_by(Hotel.name).all()
    rests = session.query(Restaurant).order_by(Restaurant.name).all()
    customers = session.query(Customer).order_by(Customer.name).all()

    hotel = st.selectbox("الفندق", hotels, format_func=lambda h: h.name if h else "")
    rest = st.selectbox("المطعم", rests, format_func=lambda r: r.name if r else "")
    cust = st.selectbox("العميل", customers, format_func=lambda c: c.name if c else "")
    booking_no = st.text_input("رقم الحجز/الفاتورة (اختياري)")
    rooms_numbers = st.text_input("أرقام الغرف (مثال: 811-816-822)")

    ci = st.date_input("تاريخ الدخول", value=date.today())
    co = st.date_input("تاريخ الخروج", value=date.today())
    nights = max((co - ci).days, 0)
    st.write("عدد الليالي:", nights)

    col1, col2, col3 = st.columns(3)
    with col1:
        rooms = st.number_input("عدد الغرف", min_value=0, step=1)
    with col2:
        room_price = st.number_input("سعر الغرفة", min_value=0.0, step=1.0)
    with col3:
        rooms_total = rooms * nights * room_price
        st.metric("إجمالي الغرف", f"{rooms_total:,.2f}")

    st.markdown("### الوجبات (مطاعم خارجية)")
    tiers = session.query(MealTier).filter(MealTier.restaurant_id==(rest.id if rest else -1)).all()
    base_days = st.number_input("عدد أيام الوجبات الأساسية", min_value=0, step=1)
    base_inputs = []
    base_total = 0.0
    for t in tiers:
        persons = st.number_input(f"{t.name} - عدد الأشخاص الأساسيين", min_value=0, step=1, key=f"base_{t.id}")
        base_inputs.append({"tier_id": t.id, "tier_name": t.name, "persons": persons, "daily_price": t.daily_price})
        base_total += persons * base_days * t.daily_price

    st.markdown("#### إضافات وجبات (بالشخص/بالوجبة/باليوم)")
    extra_meals_per_day = st.number_input("عدد الوجبات الإضافية/اليوم للشخص", min_value=0, step=1, value=0)
    extra_days = st.number_input("عدد أيام الوجبات الإضافية", min_value=0, step=1, value=0)
    extra_inputs = []
    extra_total = 0.0
    for t in tiers:
        persons_extra = st.number_input(f"{t.name} - أشخاص بوجبات إضافية", min_value=0, step=1, key=f"extra_{t.id}")
        price_one_meal = (t.daily_price/3.0) if t.daily_price else 0.0
        extra_total += persons_extra * extra_meals_per_day * extra_days * price_one_meal
        extra_inputs.append({"tier_id": t.id, "tier_name": t.name, "persons_extra": persons_extra, "price_one_meal": price_one_meal})

    st.markdown("#### خصم وجبات (أشخاص بدون وجبات)")
    no_meal_days = st.number_input("عدد الأيام بدون وجبات", min_value=0, step=1, value=0)
    no_meal_inputs = []
    no_meal_total = 0.0
    for t in tiers:
        persons_no = st.number_input(f"{t.name} - أشخاص بدون وجبات", min_value=0, step=1, key=f"no_{t.id}")
        no_meal_total += persons_no * no_meal_days * t.daily_price
        no_meal_inputs.append({"tier_id": t.id, "tier_name": t.name, "persons_no": persons_no})

    meals_total = base_total + extra_total - no_meal_total
    st.metric("إجمالي الوجبات", f"{meals_total:,.2f}")

    paid = st.number_input("المدفوع", min_value=0.0, step=1.0, value=0.0)
    total = rooms_total + meals_total
    balance = total - paid
    st.metric("الإجمالي", f"{total:,.2f}")
    st.metric("المتبقي", f"{balance:,.2f}")
    notes = st.text_area("ملاحظات")

    usd_rate_default = float(get_setting("DEFAULT_USD_RATE","3.7") or 3.7)
    usd_rate = st.number_input("سعر الصرف (1$ = X ر.س) — يظهر فقط بالفاتورة", min_value=0.1, step=0.1, value=usd_rate_default)

    if st.button("إنشاء الحجز ✅"):
        b = Booking(
            booking_no=(booking_no.strip() or None),
            hotel_id=(hotel.id if hotel else None),
            customer_id=(cust.id if cust else None),
            restaurant_id=(rest.id if rest else None),
            check_in=ci, check_out=co, nights=nights,
            rooms=rooms, room_price=room_price, rooms_total=rooms_total,
            rooms_numbers=rooms_numbers.strip() or None,
            meals_total=meals_total,
            total=total, paid=paid, balance=balance,
            notes=notes.strip() or None,
            meals_json=json.dumps({
                "base_days": base_days,
                "base_inputs": base_inputs,
                "extra_meals_per_day": extra_meals_per_day,
                "extra_days": extra_days,
                "extra_inputs": extra_inputs,
                "no_meal_days": no_meal_days,
                "no_meal_inputs": no_meal_inputs,
            }, ensure_ascii=False)
        )
        session.add(b); session.commit()
        set_setting("DEFAULT_USD_RATE", str(usd_rate))
        st.success("تم إنشاء الحجز")

    st.divider()
    if st.button("🖨 طباعة فاتورة آخر حجز (PDF: ريال + دولار)"):
        b = session.query(Booking).order_by(Booking.id.desc()).first()
        if not b:
            st.warning("لا توجد حجوزات بعد")
        else:
            usd_rate = float(get_setting("DEFAULT_USD_RATE","3.7") or 3.7)
            lines = [
                ("غرف: عدد × ليالي × سعر", b.rooms_total, b.rooms_total/usd_rate if usd_rate else 0),
                ("وجبات (أساسي/إضافي/خصم)", b.meals_total, b.meals_total/usd_rate if usd_rate else 0),
            ]
            meta = {
                "company_name": get_setting("COMPANY_NAME",""),
                "vat_id": get_setting("COMPANY_VAT_ID",""),
                "address": get_setting("COMPANY_ADDRESS",""),
                "phone": get_setting("COMPANY_PHONE",""),
                "invoice_no": b.booking_no or str(b.id),
                "date_str": date.today().strftime("%d/%m/%Y"),
                "customer": (b.customer.name if b.customer else ""),
                "usd_rate": usd_rate,
                "total_sar": b.total,
                "total_usd": (b.total/usd_rate) if usd_rate else 0,
                "note": "تم تمديد الإقامة على نفس الحجز للفترة المذكورة" if (b.notes and "تم تمديد" in b.notes) else "",
                "extension_note": "تم تمديد الإقامة على نفس الحجز للفترة المذكورة" if (b.notes and "تم تمديد" in b.notes) else ""
            }
            out = os.path.join(EXPORTS, f"invoice_{b.id}.pdf")
            make_invoice_pdf(out, LOGO, meta, lines)
            st.success(f"تم إنشاء الفاتورة: {out}")

with tabs[6]:
    st.subheader("التقارير والتصدير")
    qs = session.query(Booking).order_by(Booking.id).all()
    base = []
    for b in qs:
        base.append({
            "ID": b.id,
            "حجز": b.booking_no or b.id,
            "فندق": b.hotel.name if b.hotel else "",
            "مطعم": b.restaurant.name if b.restaurant else "",
            "عميل": b.customer.name if b.customer else "",
            "غرف (SAR)": b.rooms_total,
            "وجبات (SAR)": b.meals_total,
            "الإجمالي (SAR)": b.total,
            "مدفوع": b.paid,
            "متبقي": b.balance,
        })
    df = pd.DataFrame(base) if base else pd.DataFrame(columns=["ID","حجز","فندق","مطعم","عميل","غرف (SAR)","وجبات (SAR)","الإجمالي (SAR)","مدفوع","متبقي"])
    st.dataframe(df, use_container_width=True)
    if st.button("📤 تصدير تقرير عام إلى Excel"):
        xlsx_path = os.path.join(EXPORTS, "report_overview.xlsx")
        df.to_excel(xlsx_path, index=False)
        st.success(f"تم إنشاء الملف: {xlsx_path}")

with tabs[7]:
    st.subheader("السندات المالية")
    st.caption("ترقيم السندات: أرقام فقط (1،2،3…) وطريقة الدفع نقدًا فقط كما طلبت")

    colA, colB = st.columns(2)

    # سند استلام نقدية
    with colA:
        st.markdown("### 🟢 سند استلام نقدية (Receipt)")
        rcpt_no = int(get_setting("NEXT_RCPT_NO","1") or "1")
        st.text_input("رقم السند (تلقائي)", value=str(rcpt_no), disabled=True, key="receipt_no")
        r_amount = st.number_input("المبلغ (ر.س)", min_value=0.0, step=1.0, key="receipt_amount")
        r_party = st.text_input("من العميل/الجهة")
        r_for = st.text_input("مقابل (اختياري)", key="receipt_for")

        if st.button("حفظ سند استلام ✅"):
            if r_party.strip() and r_amount > 0:
                v = Voucher(vtype="receipt", number=str(rcpt_no), amount=r_amount, party=r_party.strip(), notes=r_for.strip() or None)
                session.add(v)
                session.commit()
                set_setting("NEXT_RCPT_NO", str(rcpt_no + 1))

                out = os.path.join(EXPORTS, f"receipt_{v.id}.pdf")
                make_voucher_pdf(out, LOGO, {
                    "type": "receipt",
                    "number": v.number,
                    "date": date.today().strftime("%d/%m/%Y"),
                    "party": v.party,
                    "amount": v.amount,
                    "purpose": r_for
                })
                st.success(f"تم حفظ السند وإنشاء PDF: {out}")

    # سند صرف نقدية
    with colB:
        st.markdown("### 🔴 سند صرف نقدية (Payment)")
        pay_no = int(get_setting("NEXT_PAY_NO","1") or "1")
        st.text_input("رقم السند (تلقائي)", value=str(pay_no), disabled=True, key="payment_no")
        p_amount = st.number_input("المبلغ (ر.س)", min_value=0.0, step=1.0, key="payment_amount")
        p_party = st.text_input("إلى الجهة/المورد")
        p_for = st.text_input("مقابل (اختياري)", key="payment_for")

        if st.button("حفظ سند صرف ✅"):
            if p_party.strip() and p_amount > 0:
                v = Voucher(vtype="payment", number=str(pay_no), amount=p_amount, party=p_party.strip(), notes=p_for.strip() or None)
                session.add(v)
                session.commit()
                set_setting("NEXT_PAY_NO", str(pay_no + 1))

                out = os.path.join(EXPORTS, f"payment_{v.id}.pdf")
                make_voucher_pdf(out, LOGO, {
                    "type": "payment",
                    "number": v.number,
                    "date": date.today().strftime("%d/%m/%Y"),
                    "party": v.party,
                    "amount": v.amount,
                    "purpose": p_for
                })
                st.success(f"تم حفظ السند وإنشاء PDF: {out}")

