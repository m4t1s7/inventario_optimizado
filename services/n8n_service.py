import json
import random
import time
from typing import Any, Dict, List, Tuple
import requests

from config import N8N_IMAGE_WEBHOOK_URL, N8N_EXCEL_WEBHOOK_URL, ENABLE_MOCK_FALLBACK

MOCK_CATALOG = [
    {"nombre": "Café Grano Especial 500g",       "codigo_barras": "7701234500018", "referencia_proveedor": "CAF-8921", "stock": 18, "stock_minimo": 5,  "precio": 12500},
    {"nombre": "Galletas Avena & Miel 250g",       "codigo_barras": "7701234500025", "referencia_proveedor": "GAL-4410", "stock": 35, "stock_minimo": 10, "precio": 3800},
    {"nombre": "Bebida Energética Citrus 473ml",   "codigo_barras": "7701234500032", "referencia_proveedor": "BEB-1093", "stock": 24, "stock_minimo": 8,  "precio": 5200},
    {"nombre": "Chocolate Amargo 70% Cacao",        "codigo_barras": "7701234500049", "referencia_proveedor": "",         "stock": 40, "stock_minimo": 12, "precio": 7900},
    {"nombre": "Snack Almendras Tostadas 120g",    "codigo_barras": "",             "referencia_proveedor": "SNK-3382", "stock": 12, "stock_minimo": 4,  "precio": 9100},
    {"nombre": "Té Verde Orgánico x20 bolsitas",   "codigo_barras": "7701234500063", "referencia_proveedor": "TE-9901",  "stock": 20, "stock_minimo": 6,  "precio": 6400},
]

def extraer_datos_imagen_n8n(image_bytes: bytes, filename: str = "foto_producto.jpg") -> Tuple[bool, List[Dict[str, Any]], str, bool]:
    """
    Envía la imagen capturada al webhook de n8n para análisis con IA.
    Retorna: (éxito, lista_de_productos, mensaje_o_error, es_modo_simulacion)
    """
    # Si no hay URL configurada o es la de ejemplo, verificar si el usuario tiene activado el fallback de prueba
    is_placeholder_url = not N8N_IMAGE_WEBHOOK_URL or "tu-instancia-n8n.com" in N8N_IMAGE_WEBHOOK_URL
    
    if is_placeholder_url:
        if ENABLE_MOCK_FALLBACK:
            # Simular tiempo de respuesta de IA (1.2 segundos) para probar UX
            time.sleep(1.2)
            item_aleatorio = random.choice(MOCK_CATALOG).copy()
            # Añadir variación de stock
            item_aleatorio["stock"] = random.randint(5, 50)
            return True, [item_aleatorio], "Detectado en Modo Simulación (Configura tu URL real de n8n en secrets)", True
        return False, [], "No se ha configurado la URL del Webhook de Imagen (N8N_IMAGE_WEBHOOK_URL).", False

    try:
        files = {
            "image": (filename, image_bytes, "image/jpeg")
        }
        data = {
            "source": "streamlit_inventory_scanner"
        }
        
        response = requests.post(
            N8N_IMAGE_WEBHOOK_URL,
            files=files,
            data=data,
            timeout=30 # La IA puede tardar unos segundos en procesar
        )
        
        if response.status_code in (200, 201):
            res_json = response.json()
            
            # Normalizar respuesta (puede ser lista o diccionario con 'nombre', 'codigo', 'stock')
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
            
            # Sanitizar campos — esquema completo de 6 campos
            lista_normalizada = []
            for p in productos:
                lista_normalizada.append({
                    "nombre":               str(p.get("nombre", p.get("name", "Producto Desconocido"))).strip(),
                    "codigo_barras":        str(p.get("codigo_barras", p.get("barcode", p.get("ean", "")))).strip(),
                    "referencia_proveedor": str(p.get("referencia_proveedor", p.get("referencia", p.get("sku", p.get("ref", ""))))).strip(),
                    "stock":               int(p.get("stock", p.get("cantidad", p.get("quantity", 1)))),
                    "stock_minimo":         int(p.get("stock_minimo", p.get("min_stock", p.get("minimo", 0)))),
                    "precio":               float(p.get("precio", p.get("price", p.get("valor", 0.0))))
                })

            if not lista_normalizada:
                return False, [], "La IA no logró detectar ningún producto legible en la foto.", False

            return True, lista_normalizada, f"Se detectaron {len(lista_normalizada)} producto(s) correctamente.", False
        
        return False, [], f"Error del servidor n8n (HTTP {response.status_code}): {response.text[:150]}", False

    except requests.exceptions.RequestException as e:
        return False, [], f"Error de conexión con n8n: {str(e)}", False
    except Exception as e:
        return False, [], f"Error al procesar la respuesta: {str(e)}", False


def enviar_datos_a_excel_n8n(productos: List[Dict[str, Any]]) -> Tuple[bool, str, bool]:
    """
    Envía la tabla de productos confirmados al webhook de n8n para guardarse en Excel.
    Retorna: (éxito, mensaje, es_modo_simulacion)
    """
    if not productos:
        return False, "La tabla está vacía. No hay datos para enviar.", False

    is_placeholder_url = not N8N_EXCEL_WEBHOOK_URL or "tu-instancia-n8n.com" in N8N_EXCEL_WEBHOOK_URL

    if is_placeholder_url:
        if ENABLE_MOCK_FALLBACK:
            time.sleep(1.0)
            return True, f"¡Éxito simulado! Se confirmaron {len(productos)} productos para Excel.", True
        return False, "No se ha configurado la URL del Webhook de Excel (N8N_EXCEL_WEBHOOK_URL).", False

    try:
        payload = {
            "evento": "confirmacion_inventario",
            "total_items": len(productos),
            "productos": productos
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            N8N_EXCEL_WEBHOOK_URL,
            data=json.dumps(payload),
            headers=headers,
            timeout=25
        )

        if response.status_code in (200, 201):
            return True, f"¡{len(productos)} registros enviados y organizados en Excel con éxito!", False
        
        return False, f"Error en webhook de Excel (HTTP {response.status_code}): {response.text[:150]}", False

    except requests.exceptions.RequestException as e:
        return False, f"Fallo al conectar con n8n Excel: {str(e)}", False
    except Exception as e:
        return False, f"Error inesperado: {str(e)}", False
