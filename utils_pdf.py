
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

def draw_watermark(c, logo_path, opacity=0.1, scale=0.6):
    try:
        c.saveState()
        c.setFillAlpha(opacity)
        w, h = A4
        img = ImageReader(logo_path)
        iw, ih = img.getSize()
        ratio = (w*scale)/iw
        c.drawImage(img, (w - iw*ratio)/2, (h - ih*ratio)/2, iw*ratio, ih*ratio, mask='auto', preserveAspectRatio=True)
        c.restoreState()
    except Exception:
        pass

def currency_fmt(v):
    try:
        return f"{float(v):,.2f}"
    except:
        return str(v)

def make_invoice_pdf(path, logo_path, meta, lines):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4

    if logo_path and os.path.exists(logo_path):
        draw_watermark(c, logo_path, 0.08, 0.8)
        img = ImageReader(logo_path)
        c.drawImage(img, w-40*mm, h-25*mm, 30*mm, 20*mm, preserveAspectRatio=True, mask='auto')

    # company block
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(w-45*mm, h-10*mm, meta.get("company_name",""))
    c.setFont("Helvetica", 9)
    c.drawRightString(w-45*mm, h-15*mm, f"VAT: {meta.get('vat_id','')}")
    c.drawRightString(w-45*mm, h-19*mm, meta.get("address",""))
    c.drawRightString(w-45*mm, h-23*mm, meta.get("phone",""))

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w/2, h-35*mm, "فاتورة / INVOICE")

    c.setFont("Helvetica", 10)
    c.drawString(15*mm, h-45*mm, f"رقم الفاتورة: {meta.get('invoice_no','')}")
    c.drawString(80*mm, h-45*mm, f"التاريخ: {meta.get('date_str','')}")
    c.drawString(15*mm, h-51*mm, f"العميل/الشركة: {meta.get('customer','')}")
    c.drawString(15*mm, h-57*mm, f"ملاحظة: {meta.get('note','')}")
    c.drawString(15*mm, h-63*mm, f"سعر الصرف: 1$ = {meta.get('usd_rate','')} ر.س")

    y = h-75*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(15*mm, y, "البيان / Description")
    c.drawRightString(w-80*mm, y, "المبلغ (ر.س)")
    c.drawRightString(w-25*mm, y, "Amount ($)")
    c.line(12*mm, y-2*mm, w-12*mm, y-2*mm)
    y -= 7*mm

    c.setFont("Helvetica", 10)
    for label, sar, usd in lines:
        c.drawString(15*mm, y, str(label))
        c.drawRightString(w-80*mm, y, currency_fmt(sar))
        c.drawRightString(w-25*mm, y, currency_fmt(usd))
        y -= 6*mm
        if y < 30*mm:
            c.showPage()
            y = h-20*mm

    y -= 2*mm
    c.line(12*mm, y, w-12*mm, y)
    y -= 8*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(15*mm, y, "الإجمالي / Total")
    c.drawRightString(w-80*mm, y, currency_fmt(meta.get("total_sar",0)))
    c.drawRightString(w-25*mm, y, currency_fmt(meta.get("total_usd",0)))

    y -= 10*mm
    if meta.get("extension_note"):
        c.setFont("Helvetica", 9)
        c.drawString(15*mm, y, meta["extension_note"])

    c.showPage()
    c.save()

import os
def make_voucher_pdf(path, logo_path, meta):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader

    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4

    if logo_path and os.path.exists(logo_path):
        draw_watermark(c, logo_path, 0.06, 0.9)
        img = ImageReader(logo_path)
        c.drawImage(img, w-40*mm, h-25*mm, 30*mm, 20*mm, preserveAspectRatio=True, mask='auto')

    title = "سند استلام نقدية" if meta.get("type")=="receipt" else "سند صرف نقدية"
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w/2, h-35*mm, title)

    c.setFont("Helvetica", 11)
    c.drawString(20*mm, h-50*mm, f"رقم السند: {meta.get('number','')}")
    c.drawString(100*mm, h-50*mm, f"التاريخ: {meta.get('date','')}")
    c.drawString(20*mm, h-60*mm, f"الجهة: {meta.get('party','')}")
    c.drawString(20*mm, h-70*mm, f"المبلغ: {meta.get('amount',0):,.2f} ر.س (نقداً)")
    if meta.get("purpose"):
        c.drawString(20*mm, h-80*mm, f"مقابل: {meta.get('purpose')}")

    c.setFont("Helvetica", 10)
    c.drawString(20*mm, 40*mm, "توقيع المحاسب: ___________________")
    c.drawString(110*mm, 40*mm, "توقيع المستلم: ___________________")
    c.drawString(20*mm, 30*mm, "الختم: ___________________")

    c.showPage()
    c.save()
