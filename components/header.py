import streamlit as st
from config import N8N_IMAGE_WEBHOOK_URL, N8N_EXCEL_WEBHOOK_URL

def render_header():
    """
    Renderiza el encabezado estilizado con el estado de conexión de los webhooks.
    """
    col_titulo, col_estado = st.columns([3, 1.2])

    with col_titulo:
        st.markdown(
            """
            <div class="header-title">
                <span>📦</span> Smart Inventory AI Scanner
            </div>
            <div class="header-subtitle">
                Captura productos con la cámara, analiza con IA mediante n8n y exporta a Excel con un clic.
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col_estado:
        tiene_url_imagen = bool(N8N_IMAGE_WEBHOOK_URL and "tu-instancia-n8n.com" not in N8N_IMAGE_WEBHOOK_URL)
        tiene_url_excel = bool(N8N_EXCEL_WEBHOOK_URL and "tu-instancia-n8n.com" not in N8N_EXCEL_WEBHOOK_URL)
        
        if tiene_url_imagen and tiene_url_excel:
            badge_html = """
            <div style="text-align: right; margin-top: 10px;">
                <span class="status-badge badge-live">
                    <span class="pulsing-dot"></span> n8n Conectado
                </span>
            </div>
            """
        else:
            badge_html = """
            <div style="text-align: right; margin-top: 10px;">
                <span class="status-badge badge-demo">
                    <span class="pulsing-dot"></span> Sin webhooks configurados
                </span>
            </div>
            """
        st.markdown(badge_html, unsafe_allow_html=True)
