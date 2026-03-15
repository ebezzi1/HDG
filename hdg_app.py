"""
HDG Quality Control — Main Application Entry Point

Multi-page Streamlit app for the Hot Dip Galvanizing chemical management system.

Run with:
    streamlit run tools/hdg_app.py
"""

import streamlit as st

st.set_page_config(
    page_title="HDG Quality Control",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown("### ⚗️ HDG QC System")
    st.caption("Hot Dip Galvanizing\nQuality Control")
    st.divider()

pg = st.navigation([
    st.Page("pages/dashboard.py",      title="Dashboard",      icon="🏭", default=True),
    st.Page("pages/operations.py",     title="Operations",     icon="⚗️"),
    st.Page("pages/history.py",        title="History",        icon="📋"),
    st.Page("pages/knowledge_base.py", title="Knowledge Base", icon="📖"),
])

pg.run()
