import streamlit as st
from services.n8n_service import extraer_datos_imagen_n8n

def render_camera_section():
    """
    Renderiza el centro de escaneo con soporte para Cámara en vivo y Subida manual de imagen.
    """
    with st.container(border=True):
        st.markdown("### 📸 Centro de Escaneo")
        st.caption("Toma una fotografía directa del producto, etiqueta o estantería.")

        tab_camara, tab_archivo = st.tabs(["📷 Cámara en Vivo", "📁 Subir Imagen"])
        
        imagen_capturada = None
        origen = ""

        with tab_camara:
            foto_camara = st.camera_input("Enfoca el producto o código", label_visibility="collapsed")
            if foto_camara:
                imagen_capturada = foto_camara
                origen = "camara"

        with tab_archivo:
            archivo_subido = st.file_uploader(
                "O selecciona una foto de tu dispositivo", 
                type=["jpg", "jpeg", "png", "webp"],
                help="Útil si ya tomaste la foto o estás probando desde la computadora."
            )
            if archivo_subido:
                imagen_capturada = archivo_subido
                origen = "archivo"

        # Si hay imagen, ofrecer botón desplegable para inspeccionarla en grande
        if imagen_capturada:
            with st.expander("🔍 Ver foto en grande / Zoom", expanded=False):
                st.image(imagen_capturada, caption="Foto lista para enviar", use_container_width=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Botón de Procesar con IA
        col_btn1, col_btn2 = st.columns([1.5, 1])
        with col_btn1:
            boton_procesar = st.button(
                "Analizar con IA y Agregar", 
                type="primary", 
                use_container_width=True,
                disabled=(imagen_capturada is None)
            )

        with col_btn2:
            if imagen_capturada is None:
                st.info("Esperando captura...")
            else:
                st.success("Foto lista", icon="✅")

        # Acción al presionar el botón
        if boton_procesar and imagen_capturada:
            with st.spinner("La IA está analizando la imagen y extrayendo los datos..."):
                bytes_imagen = imagen_capturada.getvalue()
                nombre_archivo = f"{origen}_{imagen_capturada.name}" if hasattr(imagen_capturada, 'name') else "scan.jpg"
                
                exito, productos_extraidos, mensaje, es_mock = extraer_datos_imagen_n8n(bytes_imagen, nombre_archivo)

                if exito:
                    # Anexar a la lista existente en sesión
                    for prod in productos_extraidos:
                        st.session_state["inventory_data"].append(prod)
                    
                    st.toast(f"🎉 ¡{len(productos_extraidos)} producto(s) añadidos a la tabla!", icon="✨")
                    
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(f"❌ {mensaje}")
