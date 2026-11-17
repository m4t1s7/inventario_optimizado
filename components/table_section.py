import streamlit as st
import pandas as pd
from services.n8n_service import enviar_datos_a_excel_n8n


def _limpiar_texto(val) -> str:
    """Convierte None, NaN de pandas o textos 'nan'/'none' en cadena vacía ''."""
    if val is None or pd.isna(val):
        return ""
    texto = str(val).strip()
    return "" if texto.lower() in ("nan", "none", "null") else texto


def render_table_section(modo: str = "ingreso"):
    """
    Renderiza la tabla interactiva de inventario editable, las métricas acumuladas
    y el botón de confirmación para sincronizar con Excel vía n8n.
    modo: "ingreso" (6 columnas) | "salida" (4 columnas)
    """
    es_salida = (modo == "salida")
    accion = "egreso" if es_salida else "ingreso"
    session_key = "inventory_data_salida" if es_salida else "inventory_data_ingreso"

    if session_key not in st.session_state:
        st.session_state[session_key] = []

    with st.container(border=True):
        if es_salida:
            st.markdown("### 📋 Tabla de Salida / Ventas Verificada")
            st.caption("Revisa los productos y las unidades vendidas antes de descontar del inventario.")
        else:
            st.markdown("### 📋 Tabla de Inventario Verificada (Ingreso)")
            st.caption("Revisa o corrige cualquier dato haciendo doble clic en la celda antes de confirmar.")

        datos_actuales = st.session_state.get(session_key, [])
        
        # Métricas resumidas superiores
        total_items = len(datos_actuales)
        if es_salida:
            total_unidades = sum(int(item.get("cantidad_salida", item.get("stock", 0)) or 0) for item in datos_actuales)
            label_unidades = "📉 Unidades a Descontar"
        else:
            total_unidades = sum(int(item.get("stock", 0) or 0) for item in datos_actuales)
            label_unidades = "📊 Stock Total Acumulado"

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(label="📦 Productos Registrados", value=f"{total_items} ítems")
        with col_m2:
            st.metric(label=label_unidades, value=f"{total_unidades} uds")
        with col_m3:
            estado_label = "Listo para enviar" if total_items > 0 else "Sin registros"
            st.metric(label="⚡ Estado", value=estado_label)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        if es_salida:
            columnas_esperadas = ["nombre", "codigo_barras", "referencia_proveedor", "cantidad_salida"]
            config_columnas = {
                "nombre":               st.column_config.TextColumn("Nombre del Producto",  required=True,  width="large"),
                "codigo_barras":        st.column_config.TextColumn("Cód. Barras",          required=False, width="small", help="EAN-13 u otro código de barras"),
                "referencia_proveedor": st.column_config.TextColumn("Ref. Proveedor",       required=False, width="small", help="Código interno del proveedor"),
                "cantidad_salida":      st.column_config.NumberColumn("Cant. Vendida",      min_value=1, step=1, required=True, default=1, width="small"),
            }
        else:
            columnas_esperadas = ["nombre", "codigo_barras", "referencia_proveedor", "stock", "stock_minimo", "precio"]
            config_columnas = {
                "nombre":               st.column_config.TextColumn("Nombre del Producto",  required=True,  width="large"),
                "codigo_barras":        st.column_config.TextColumn("Cód. Barras",          required=False, width="small",  help="EAN-13 u otro código de barras"),
                "referencia_proveedor": st.column_config.TextColumn("Ref. Proveedor",       required=False, width="small",  help="Código interno del proveedor"),
                "stock":                st.column_config.NumberColumn("Stock",              min_value=0, step=1,    required=True,  default=1,   width="small"),
                "stock_minimo":         st.column_config.NumberColumn("Stock Mín.",         min_value=0, step=1,    required=False, default=0,   width="small"),
                "precio":               st.column_config.NumberColumn("Precio",             min_value=0, step=0.01, required=False, default=0.0, width="small", format="%.2f"),
            }

        if not datos_actuales:
            st.info("ℹ️ Aún no hay productos en la tabla. Toma una foto en el panel izquierdo para añadir registros automáticamente.", icon="📷")
            df_vacio = pd.DataFrame(columns=columnas_esperadas)
            df_editado = st.data_editor(
                df_vacio,
                num_rows="dynamic",
                use_container_width=True,
                column_config=config_columnas,
                key=f"empty_editor_{modo}"
            )
            if not df_editado.empty:
                st.session_state[session_key] = df_editado.fillna("").to_dict(orient="records")
                st.rerun()
            return

        # --- Migración de esquema según el modo ---
        datos_migrados = []
        for item in datos_actuales:
            if es_salida:
                cant_val = item.get("cantidad_salida", item.get("cantidad_vendida", item.get("stock", 1)))
                datos_migrados.append({
                    "nombre":               _limpiar_texto(item.get("nombre", "")),
                    "codigo_barras":        _limpiar_texto(item.get("codigo_barras", item.get("barcode", ""))),
                    "referencia_proveedor": _limpiar_texto(item.get("referencia_proveedor", item.get("codigo", ""))),
                    "cantidad_salida":      int(cant_val if pd.notna(cant_val) and cant_val is not None and str(cant_val) != "" else 1),
                })
            else:
                stock_val = item.get("stock", 0)
                min_val = item.get("stock_minimo", item.get("min_stock", 0))
                precio_val = item.get("precio", item.get("price", 0.0))
                datos_migrados.append({
                    "nombre":               _limpiar_texto(item.get("nombre", "")),
                    "codigo_barras":        _limpiar_texto(item.get("codigo_barras", item.get("barcode", ""))),
                    "referencia_proveedor": _limpiar_texto(item.get("referencia_proveedor", item.get("codigo", ""))),
                    "stock":                int(stock_val if pd.notna(stock_val) and stock_val is not None and str(stock_val) != "" else 0),
                    "stock_minimo":         int(min_val if pd.notna(min_val) and min_val is not None and str(min_val) != "" else 0),
                    "precio":               float(precio_val if pd.notna(precio_val) and precio_val is not None and str(precio_val) != "" else 0.0),
                })

        if datos_migrados != datos_actuales:
            st.session_state[session_key] = datos_migrados
            datos_actuales = datos_migrados

        df = pd.DataFrame(datos_migrados, columns=columnas_esperadas)

        df_editado = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config=config_columnas,
            key=f"inventory_editor_{modo}"
        )

        # Limpiar cualquier NaN que pandas genere al agregar o editar filas
        registros_editados = df_editado.to_dict(orient="records")
        datos_actualizados = []
        for reg in registros_editados:
            if es_salida:
                c_val = reg.get("cantidad_salida", 1)
                datos_actualizados.append({
                    "nombre":               _limpiar_texto(reg.get("nombre", "")),
                    "codigo_barras":        _limpiar_texto(reg.get("codigo_barras", "")),
                    "referencia_proveedor": _limpiar_texto(reg.get("referencia_proveedor", "")),
                    "cantidad_salida":      int(c_val if pd.notna(c_val) and c_val is not None and str(c_val) != "" else 1),
                })
            else:
                s_val = reg.get("stock", 0)
                m_val = reg.get("stock_minimo", 0)
                p_val = reg.get("precio", 0.0)
                datos_actualizados.append({
                    "nombre":               _limpiar_texto(reg.get("nombre", "")),
                    "codigo_barras":        _limpiar_texto(reg.get("codigo_barras", "")),
                    "referencia_proveedor": _limpiar_texto(reg.get("referencia_proveedor", "")),
                    "stock":                int(s_val if pd.notna(s_val) and s_val is not None and str(s_val) != "" else 0),
                    "stock_minimo":         int(m_val if pd.notna(m_val) and m_val is not None and str(m_val) != "" else 0),
                    "precio":               float(p_val if pd.notna(p_val) and p_val is not None and str(p_val) != "" else 0.0),
                })

        if datos_actualizados != datos_actuales:
            st.session_state[session_key] = datos_actualizados

        # Validar que cada producto tenga al menos uno de los dos códigos
        productos_sin_codigo = []
        for idx, item in enumerate(st.session_state[session_key], start=1):
            cod_barras = str(item.get("codigo_barras") or "").strip()
            if cod_barras.lower() == "nan":
                cod_barras = ""
            ref_prov = str(item.get("referencia_proveedor") or "").strip()
            if ref_prov.lower() == "nan":
                ref_prov = ""
            if not cod_barras and not ref_prov:
                nombre_prod = str(item.get("nombre") or f"Fila #{idx}").strip()
                productos_sin_codigo.append(f"Fila {idx} ({nombre_prod})")

        if productos_sin_codigo:
            st.warning(
                f"⚠️ **Falta código identificador:** Cada producto debe tener al menos **Cód. Barras** o **Ref. Proveedor**. "
                f"Revisa: {', '.join(productos_sin_codigo)}."
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        col_accion_secundaria, col_accion_primaria = st.columns([1, 1.6])

        with col_accion_secundaria:
            if st.button("🗑️ Vaciar Tabla", type="secondary", use_container_width=True, key=f"btn_vaciar_{modo}"):
                st.session_state[session_key] = []
                st.toast("Tabla vaciada.", icon="🧹")
                st.rerun()

        with col_accion_primaria:
            texto_boton = "🚀 Confirmar y Descontar Stock" if es_salida else "🚀 Confirmar y Enviar a Excel"
            boton_confirmar = st.button(
                texto_boton, 
                type="primary", 
                use_container_width=True,
                disabled=(total_items == 0),
                key=f"btn_confirmar_{modo}"
            )

        if boton_confirmar:
            if productos_sin_codigo:
                st.error(
                    f"❌ No se puede enviar a Excel: {len(productos_sin_codigo)} producto(s) no tienen ni Código de Barras ni Ref. Proveedor ({', '.join(productos_sin_codigo)}). Completa al menos uno en la tabla."
                )
            else:
                with st.spinner("📤 Enviando datos confirmados a n8n para actualizar Excel..."):
                    exito, mensaje, es_mock = enviar_datos_a_excel_n8n(
                        st.session_state[session_key],
                        accion=accion
                    )
                    
                    if exito:
                        st.balloons()
                        st.toast("✅ ¡Operación sincronizada con Excel exitosamente!", icon="🎉")
                        st.success(mensaje)
                        st.info("💡 Puedes vaciar la tabla para iniciar un nuevo lote de escaneo cuando gustes.")
                    else:
                        st.error(f"❌ {mensaje}")
