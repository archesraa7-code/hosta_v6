import streamlit as st
import sqlite3

st.set_page_config(page_title="Hotel Ops Pro", page_icon="🏨", layout="wide")
# --- Mobile Responsive Styles ---
st.markdown("""
<style>
/* اجعل العرض كامل على الموبايل */
@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }
    .stSidebar {
        width: 220px !important;
    }
    h1, h2, h3 {
        font-size: 1.6rem !important;
    }
    .stButton>button, .stSelectbox, .stTextInput>div>div>input {
        font-size: 1rem !important;
    }
}
/* اجبار القائمة الجانبية أنها تطوى تلقائياً على الشاشات الصغيرة */
@media (max-width: 700px) {
    [data-testid="stSidebar"] {
        transform: translateX(-100%);
        position: fixed !important;
        z-index: 999 !important;
        background: #111 !important;
        transition: 0.3s;
    }
    [data-testid="stSidebar"]:hover {
        transform: translateX(0);
    }
}
</style>
""", unsafe_allow_html=True)
# RTL if Arabic
if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"

rtl = (st.session_state["lang"] == "ar")

if rtl:
    st.markdown("""
    <style>
    html, body, [class^='css'] { direction: RTL; text-align:right; font-family: 'Cairo', sans-serif; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    html, body, [class^='css'] { direction: LTR; text-align:left; font-family: 'Cairo', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("القائمة" if rtl else "Menu")

# لغة الواجهة
if st.sidebar.button("English 🇬🇧" if rtl else "العربية 🇸🇦"):
    st.session_state["lang"] = "en" if rtl else "ar"
    st.experimental_rerun()

st.title("🏨 نظام إدارة تشغيل الفنادق و المطاعم")

st.write("""
مرحباً 👋  
اختر صفحة من القائمة الجانبية.
""" if rtl else """
Welcome 👋  
Select a page from the sidebar.
""")
