import streamlit as st


st.set_page_config(
    page_title="AI Inventory Scanner | Streamlit + n8n",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


from styles.custom_css import load_custom_css
load_custom_css()


if "inventory_data" not in st.session_state:
    st.session_state["inventory_data"] = []


from components.header import render_header
from components.camera_section import render_camera_section
from components.table_section import render_table_section
from config import N8N_IMAGE_WEBHOOK_URL, N8N_EXCEL_WEBHOOK_URL


with st.sidebar:
    st.markdown("### ⚙️ Configuración y Estado")
    st.markdown("Los webhooks están protegidos en `.streamlit/secrets.toml` o `.env`.")
    
    with st.expander("🔍 Ver estado de Webhooks", expanded=False):
        st.caption("**Webhook 1 (Análisis Imagen):**")
        if N8N_IMAGE_WEBHOOK_URL:
            st.code(N8N_IMAGE_WEBHOOK_URL[:35] + "...", language="text")
        else:
            st.warning("Sin configurar")

        st.caption("**Webhook 2 (Exportar Excel):**")
        if N8N_EXCEL_WEBHOOK_URL:
            st.code(N8N_EXCEL_WEBHOOK_URL[:35] + "...", language="text")
        else:
            st.warning("Sin configurar")

    st.markdown("---")
    st.markdown("### 💡 Instrucciones:")
    st.markdown(
        """
        1. **Sube o captura la foto** de tu factura en el panel izquierdo.
        2. Presiona **✨ Analizar con IA y Agregar**.
        3. Si la IA tuvo algún error, **edita la celda directamente** en la tabla.
        4. Haz clic en **🚀 Confirmar y Enviar a Excel** para procesar el lote.
        """
    )
    st.caption("Hecho con modularidad para Streamlit + n8n.")


render_header()

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)


col_escaneo, col_tabla = st.columns([1.1, 1.9], gap="large")

with col_escaneo:
    render_camera_section()

with col_tabla:
    render_table_section()
