import io
import streamlit as st
from PIL import Image, ImageOps
from services.n8n_service import extraer_datos_imagen_n8n

# Soporte opcional para fotos HEIC/HEIF de iPhones si la librería está instalada
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

def optimizar_imagen(bytes_imagen: bytes, max_dimension: int = 2048, quality: int = 88) -> bytes:
    """
    Optimiza la imagen tomada con el celular:
    1. Corrige la orientación EXIF (evita que las fotos verticales salgan de lado).
    2. Reduce a un máximo de 2048px manteniendo la máxima nitidez de texto para la IA.
    3. Comprime en JPEG de alta calidad (~400KB - 800KB) para un envío ultrarrápido a n8n.
    """
    try:
        img = Image.open(io.BytesIO(bytes_imagen))
        
        # Corregir rotación del sensor del celular
        img = ImageOps.exif_transpose(img)
        
        # Convertir a RGB si viene en RGBA o modo paleta
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
            
        # Redimensionar proporcionalmente solo si supera los 2048px
        ancho, alto = img.size
        if max(ancho, alto) > max_dimension:
            if ancho > alto:
                nuevo_ancho = max_dimension
                nuevo_alto = int(alto * (max_dimension / ancho))
            else:
                nuevo_alto = max_dimension
                nuevo_ancho = int(ancho * (max_dimension / alto))
            img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        return buffer.getvalue()
    except Exception:
        # En caso de error inesperado de lectura, mantener bytes originales
        return bytes_imagen

def render_camera_section():
    """
    Renderiza el centro de carga primaria de imágenes de alta fidelidad.
    Permite subir fotos de la galería o capturadas directamente con la cámara del dispositivo.
    """
    with st.container(border=True):
        st.markdown("### 📸 Carga de Factura o Producto")
        st.caption("Sube la fotografía tomada con la cámara de tu celular o desde tu galería.")

        # Carga principal de archivos (soporta todos los formatos de móvil y PC)
        archivo_subido = st.file_uploader(
            "Selecciona o captura una imagen", 
            type=["jpg", "jpeg", "png", "webp", "heic", "heif"],
            label_visibility="collapsed",
            help="Sube una foto clara con buena iluminación."
        )

        st.caption("💡 **Tip en celular:** Toma la foto primero con tu cámara normal y elígela aquí desde tu galería para conservar la máxima nitidez y evitar cierres de navegador.")

        imagen_capturada = archivo_subido

        # Si hay imagen, ofrecer botón desplegable para inspeccionarla en grande
        if imagen_capturada:
            with st.expander("🔍 Ver foto / Inspeccionar calidad", expanded=False):
                st.image(imagen_capturada, caption="Foto lista para analizar", use_container_width=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Botón de Procesar con IA
        col_btn1, col_btn2 = st.columns([1.5, 1])
        with col_btn1:
            boton_procesar = st.button(
                "✨ Analizar con IA y Agregar", 
                type="primary", 
                use_container_width=True,
                disabled=(imagen_capturada is None)
            )

        with col_btn2:
            if imagen_capturada is None:
                st.info("Esperando foto...")
            else:
                tamano_kb = round(len(imagen_capturada.getvalue()) / 1024, 1)
                st.success(f"Lista ({tamano_kb} KB)", icon="✅")

        # Acción al presionar el botón
        if boton_procesar and imagen_capturada:
            with st.spinner("⚡ Optimizando imagen y analizando con IA..."):
                bytes_originales = imagen_capturada.getvalue()
                
                # Optimizar compresión y resolución en memoria antes de mandar
                bytes_optimizados = optimizar_imagen(bytes_originales)
                
                nombre_archivo = f"factura_{imagen_capturada.name.split('.')[0]}.jpg" if hasattr(imagen_capturada, 'name') else "factura.jpg"
                
                exito, productos_extraidos, mensaje, es_mock = extraer_datos_imagen_n8n(bytes_optimizados, nombre_archivo)

                if exito:
                    # Anexar a la lista existente en sesión
                    for prod in productos_extraidos:
                        st.session_state["inventory_data"].append(prod)
                    
                    st.toast(f"🎉 ¡{len(productos_extraidos)} producto(s) añadidos a la tabla!", icon="✨")
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(f"❌ {mensaje}")
