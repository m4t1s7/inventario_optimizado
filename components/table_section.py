import streamlit as st
import pandas as pd
from services.n8n_service import enviar_datos_a_excel_n8n

def render_table_section():
    """
    Renderiza la tabla interactiva de inventario editable, las métricas acumuladas
    y el botón de confirmación para sincronizar con Excel vía n8n.
    """
    with st.container(border=True):
        st.markdown("### 📋 Tabla de Inventario Verificada")
        st.caption("Revisa o corrige cualquier dato haciendo doble clic en la celda antes de confirmar.")

        datos_actuales = st.session_state.get("inventory_data", [])
        
        # Métricas resumidas superiores
        total_items = len(datos_actuales)
        total_stock = sum(item.get("stock", 0) for item in datos_actuales)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: 
            st.metric(label="📦 Productos Registrados", value=f"{total_items} ítems")
        with col_m2:
            st.metric(label="📊 Stock Total Acumulado", value=f"{total_stock} uds")
        with col_m3:
            estado_label = "Listo para enviar" if total_items > 0 else "Sin registros"
            st.metric(label="⚡ Estado", value=estado_label)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        if not datos_actuales:
            st.info("ℹ️ Aún no hay productos en la tabla. Toma una foto en el panel izquierdo para añadir registros automáticamente.", icon="📷")
            df_vacio = pd.DataFrame(columns=["nombre", "codigo", "stock"])
            # Permitir agrega   r manualmente incluso si está vacío
            df_editado = st.data_editor(
                df_vacio,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "nombre": st.column_config.TextColumn("Nombre del Producto", required=True),
                    "codigo": st.column_config.TextColumn("Código / SKU", required=True),
                    "stock": st.column_config.NumberColumn("Stock", min_value=0, step=1, required=True, default=1)
                },
                key="empty_editor"
            )
            if not df_editado.empty:
                st.session_state["inventory_data"] = df_editado.to_dict(orient="records")
                st.rerun()
            return

        # Convertir a DataFrame para el editor visual de Streamlit
        df = pd.DataFrame(datos_actuales)

        # Editor de datos interactivo con validación de columnas
        df_editado = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "nombre": st.column_config.TextColumn("Nombre del Producto", required=True, width="medium"),
                "codigo": st.column_config.TextColumn("Código / SKU", required=True, width="small"),
                "stock": st.column_config.NumberColumn("Stock", min_value=0, step=1, required=True, width="small")
            },
            key="inventory_editor"
        )

        # Actualizar datos en sesión si hubo cambios manuales
        datos_actualizados = df_editado.to_dict(orient="records")
        if datos_actualizados != datos_actuales:
            st.session_state["inventory_data"] = datos_actualizados

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Barra de acciones al final de la tabla
        col_accion_secundaria, col_accion_primaria = st.columns([1, 1.6])

        with col_accion_secundaria:
            if st.button("🗑️ Vaciar Tabla", type="secondary", use_container_width=True):
                st.session_state["inventory_data"] = []
                st.toast("Tabla vaciada.", icon="🧹")
                st.rerun()

        with col_accion_primaria:
            boton_confirmar = st.button(
                "🚀 Confirmar y Enviar a Excel", 
                type="primary", 
                use_container_width=True,
                disabled=(total_items == 0)
            )

        if boton_confirmar:
            with st.spinner("📤 Enviando datos confirmados a n8n para estructurar en Excel..."):
                exito, mensaje, es_mock = enviar_datos_a_excel_n8n(st.session_state["inventory_data"])
                
                if exito:
                    st.balloons()
                    st.toast(f"✅ ¡Inventario guardado en Excel exitosamente!", icon="🎉")
                    st.success(mensaje)
                    # Opción: Si el usuario desea limpiar después de enviar
                    st.info("💡 Puedes vaciar la tabla para iniciar un nuevo lote de escaneo cuando gustes.")
                else:
                    st.error(f"❌ {mensaje}")
