import streamlit as st
from config import N8N_IMAGE_WEBHOOK_URL, N8N_EXCEL_WEBHOOK_URL

def render_header(modo: str = "ingreso"):
    """
    Renderiza el encabezado estilizado con navegación rápida y estado de conexión de los webhooks.
    modo: "ingreso" | "salida"
    """
    # Barra superior de navegación rápida entre páginas
    nav_col1, nav_col2, _ = st.columns([1.2, 1.2, 3.6])
    with nav_col1:
        st.page_link("app.py", label="📦 Ingreso de Stock", use_container_width=True)
    with nav_col2:
        st.page_link("pages/1_Salida_Ventas.py", label="📤 Salida / Ventas", use_container_width=True)

    col_titulo, col_estado = st.columns([3, 1.2])

    with col_titulo:
        if modo == "salida":
            st.markdown(
                """
                <div class="header-title">
                    <span>📤</span> Salida / Ventas — Descuento de Stock
                </div>
                <div class="header-subtitle">
                    Sube la foto del registro de ventas o salida, verifica las unidades vendidas y descuenta del inventario en Excel.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="header-title">
                    <span>📦</span> Smart Inventory AI Scanner — Ingreso
                </div>
                <div class="header-subtitle">
                    Captura facturas o productos con la cámara, analiza con IA mediante n8n y exporta ingresos a Excel con un clic.
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
