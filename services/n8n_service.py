import json
import random
import time
from typing import Any, Dict, List, Tuple
import requests

from config import (
    N8N_IMAGE_WEBHOOK_URL,
    N8N_EXCEL_WEBHOOK_URL,
    ENABLE_MOCK_FALLBACK,
)

def _clean_str(val: Any, default: str = "") -> str:
    if val is None:
        return default
    s = str(val).strip()
    return default if s.lower() in ("none", "null", "nan") else s


MOCK_CATALOG = [

    {"nombre": "Café Grano Especial 500g",       "codigo_barras": "7701234500018", "referencia_proveedor": "CAF-8921", "stock": 18, "stock_minimo": 5,  "precio": 12500},
    {"nombre": "Galletas Avena & Miel 250g",       "codigo_barras": "7701234500025", "referencia_proveedor": "GAL-4410", "stock": 35, "stock_minimo": 10, "precio": 3800},
    {"nombre": "Bebida Energética Citrus 473ml",   "codigo_barras": "7701234500032", "referencia_proveedor": "BEB-1093", "stock": 24, "stock_minimo": 8,  "precio": 5200},
    {"nombre": "Chocolate Amargo 70% Cacao",        "codigo_barras": "7701234500049", "referencia_proveedor": "",         "stock": 40, "stock_minimo": 12, "precio": 7900},
    {"nombre": "Snack Almendras Tostadas 120g",    "codigo_barras": "",             "referencia_proveedor": "SNK-3382", "stock": 12, "stock_minimo": 4,  "precio": 9100},
    {"nombre": "Té Verde Orgánico x20 bolsitas",   "codigo_barras": "7701234500063", "referencia_proveedor": "TE-9901",  "stock": 20, "stock_minimo": 6,  "precio": 6400},
]

def extraer_datos_imagen_n8n(
    image_bytes: bytes,
    filename: str = "foto_producto.jpg",
    accion: str = "ingreso",
) -> Tuple[bool, List[Dict[str, Any]], str, bool]:
    """
    Envía la imagen capturada al webhook de n8n para análisis con IA.
    accion: "ingreso" | "egreso"
    Retorna: (éxito, lista_de_productos, mensaje_o_error, es_modo_simulacion)
    """
    is_placeholder_url = not N8N_IMAGE_WEBHOOK_URL or "tu-instancia-n8n.com" in N8N_IMAGE_WEBHOOK_URL
    
    if is_placeholder_url:
        if ENABLE_MOCK_FALLBACK:
            time.sleep(1.2)
            item_aleatorio = random.choice(MOCK_CATALOG).copy()
            if accion == "egreso":
                item_salida = {
                    "nombre": item_aleatorio["nombre"],
                    "codigo_barras": item_aleatorio["codigo_barras"],
                    "referencia_proveedor": item_aleatorio["referencia_proveedor"],
                    "cantidad_salida": random.randint(1, 10),
                }
                return True, [item_salida], "Detectado en Modo Simulación (Salida / Ventas)", True
            else:
                item_aleatorio["stock"] = random.randint(5, 50)
                return True, [item_aleatorio], "Detectado en Modo Simulación (Configura tu URL real de n8n en secrets)", True
        return False, [], "No se ha configurado la URL del Webhook de Imagen (N8N_IMAGE_WEBHOOK_URL).", False

    try:
        files = {
            "image": (filename, image_bytes, "image/jpeg")
        }
        data = {
            "source": "streamlit_inventory_scanner",
            "accion": accion,
        }
        
        response = requests.post(
            N8N_IMAGE_WEBHOOK_URL,
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code in (200, 201):
            res_json = response.json()
            
            productos = []
            if isinstance(res_json, list):
                productos = res_json
            elif isinstance(res_json, dict):
                if "items" in res_json and isinstance(res_json["items"], list):
                    productos = res_json["items"]
                elif "productos" in res_json and isinstance(res_json["productos"], list):
                    productos = res_json["productos"]
                elif "nombre" in res_json:
                    productos = [res_json]
                elif "data" in res_json and isinstance(res_json["data"], list):
                    productos = res_json["data"]
            
            lista_normalizada = []
            for p in productos:
                raw_nombre = p.get("nombre") or p.get("name") or "Producto Desconocido"
                raw_barras = p.get("codigo_barras") or p.get("barcode") or p.get("ean") or ""
                raw_ref = p.get("referencia_proveedor") or p.get("referencia") or p.get("sku") or p.get("ref") or ""
                if accion == "egreso":
                    cantidad_val = p.get(
                        "cantidad_salida",
                        p.get("cantidad_vendida", p.get("cantidad", p.get("stock", p.get("quantity", 1))))
                    )
                    lista_normalizada.append({
                        "nombre":               _clean_str(raw_nombre, "Producto Desconocido"),
                        "codigo_barras":        _clean_str(raw_barras, ""),
                        "referencia_proveedor": _clean_str(raw_ref, ""),
                        "cantidad_salida":      int(cantidad_val if cantidad_val is not None else 1),
                    })
                else:
                    stock_val = p.get("stock", p.get("cantidad", p.get("quantity", 1)))
                    min_val = p.get("stock_minimo", p.get("min_stock", p.get("minimo", 0)))
                    precio_val = p.get("precio", p.get("price", p.get("valor", 0.0)))
                    lista_normalizada.append({
                        "nombre":               _clean_str(raw_nombre, "Producto Desconocido"),
                        "codigo_barras":        _clean_str(raw_barras, ""),
                        "referencia_proveedor": _clean_str(raw_ref, ""),
                        "stock":                int(stock_val if stock_val is not None else 1),
                        "stock_minimo":         int(min_val if min_val is not None else 0),
                        "precio":               float(precio_val if precio_val is not None else 0.0)
                    })

            if not lista_normalizada:
                return False, [], "La IA no logró detectar ningún producto legible en la foto.", False

            return True, lista_normalizada, f"Se detectaron {len(lista_normalizada)} producto(s) correctamente.", False
        
        return False, [], f"Error del servidor n8n (HTTP {response.status_code}): {response.text[:150]}", False

    except requests.exceptions.RequestException as e:
        return False, [], f"Error de conexión con n8n: {str(e)}", False
    except Exception as e:
        return False, [], f"Error al procesar la respuesta: {str(e)}", False


def enviar_datos_a_excel_n8n(
    productos: List[Dict[str, Any]],
    accion: str = "ingreso",
) -> Tuple[bool, str, bool, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Envía la tabla de productos confirmados al webhook único N8N_EXCEL_WEBHOOK_URL.
    accion: "ingreso" | "egreso"
    Retorna: (éxito_total, mensaje, es_modo_simulacion, lista_procesados, lista_fallidos)
    """
    if not productos:
        return False, "La tabla está vacía. No hay datos para enviar.", False, [], []

    is_placeholder_url = not N8N_EXCEL_WEBHOOK_URL or "tu-instancia-n8n.com" in N8N_EXCEL_WEBHOOK_URL

    if is_placeholder_url:
        if ENABLE_MOCK_FALLBACK:
            time.sleep(1.0)
            return (
                True,
                f"¡Éxito simulado! Se confirmaron {len(productos)} productos ({accion}) para Excel.",
                True,
                productos,
                [],
            )
        return False, "No se ha configurado la URL del Webhook de Excel (N8N_EXCEL_WEBHOOK_URL).", False, [], []

    try:
        payload = {
            "evento": "confirmacion_inventario",
            "accion": accion,
            "total_items": len(productos),
            "productos": productos
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            N8N_EXCEL_WEBHOOK_URL,
            data=json.dumps(payload),
            headers=headers,
            timeout=60
        )

        if response.status_code in (200, 201):
            try:
                res_json = response.json()
                if isinstance(res_json, list) and len(res_json) > 0:
                    res_json = res_json[0]
            except Exception:
                res_json = None

            if isinstance(res_json, dict):
                procesados = res_json.get("procesados", [])
                if not isinstance(procesados, list):
                    procesados = []
                fallidos = res_json.get("fallidos", [])
                if not isinstance(fallidos, list):
                    fallidos = []

                ok_flag = bool(res_json.get("ok", len(fallidos) == 0))
                mensaje_srv = str(res_json.get("mensaje") or "").strip()

                if ok_flag and len(fallidos) == 0:
                    total_ok = len(procesados) if procesados else len(productos)
                    msg = mensaje_srv or f"¡{total_ok} producto(s) sincronizados en Excel con éxito!"
                    return True, msg, False, procesados or productos, []
                else:
                    msg = (
                        f"Se procesaron {len(procesados)} producto(s) correctamente, "
                        f"pero {len(fallidos)} producto(s) no pudieron procesarse."
                    )
                    return False, msg, False, procesados, fallidos

            return True, f"¡{len(productos)} registros enviados y procesados en Excel con éxito!", False, productos, []
        
        return False, f"Error en webhook de Excel (HTTP {response.status_code}): {response.text[:150]}", False, [], []

    except requests.exceptions.RequestException as e:
        return False, f"Fallo al conectar con n8n Excel: {str(e)}", False, [], []
    except Exception as e:
        return False, f"Error inesperado: {str(e)}", False, [], []
