import streamlit as st


st.set_page_config(
    page_title="Ingreso de Stock | AI Inventory Scanner",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


from styles.custom_css import load_custom_css
load_custom_css()


if "inventory_data_ingreso" not in st.session_state:
    # Migrar si existía la clave antigua
    st.session_state["inventory_data_ingreso"] = st.session_state.get("inventory_data", [])


from components.header import render_header
from components.camera_section import render_camera_section
from components.table_section import render_table_section


render_header(modo="ingreso")

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)


col_escaneo, col_tabla = st.columns([1.1, 1.9], gap="large")

with col_escaneo:
    render_camera_section(modo="ingreso")

with col_tabla:
    render_table_section(modo="ingreso")
