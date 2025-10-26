import streamlit as st
import sqlite3

st.set_page_config(page_title="Hotel Ops Pro", page_icon="🏨", layout="wide")

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
