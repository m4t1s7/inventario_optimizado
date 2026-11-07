import json
import random
import time
from typing import Any, Dict, List, Tuple
import requests

from config import N8N_IMAGE_WEBHOOK_URL, N8N_EXCEL_WEBHOOK_URL



def extraer_datos_imagen_n8n(image_bytes: bytes, filename: str = "foto_producto.jpg") -> Tuple[bool, List[Dict[str, Any]], str, bool]:
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
            
            # Extraer lista de productos (compatible con tu nodo de n8n)
            productos = res_json.get("productos", []) if isinstance(res_json, dict) else res_json
            
            # Sanitizar campos y manejar posibles valores null (None)
            lista_normalizada = []
            for p in productos:
                # Manejar nombre seguro
                nombre_val = p.get("nombre") or "Producto Desconocido"
                
                # Si el código es null en n8n, asignamos "S/C" (Sin Código) en vez del texto "None"
                codigo_val = p.get("codigo") or "S/C"
                
                # Si el stock viene null o string, asegurar número entero
                stock_raw = p.get("stock") if p.get("stock") is not None else p.get("cantidad", 1)
                try:
                    stock_val = int(stock_raw)
                except (ValueError, TypeError):
                    stock_val = 1

                # Stock Mínimo (por defecto 0 para que el usuario lo edite en la tabla si la IA no lo trae)
                stock_min_raw = p.get("stock_minimo") or p.get("minimo_stock") or p.get("min_stock") or 0
                try:
                    stock_min_val = int(stock_min_raw)
                except (ValueError, TypeError):
                    stock_min_val = 0

                # Precio (captura el precio de la factura si viene; si no, 0.0 para editar)
                precio_raw = p.get("precio") or p.get("price") or p.get("valor") or 0.0
                try:
                    precio_val = float(precio_raw)
                except (ValueError, TypeError):
                    precio_val = 0.0

                lista_normalizada.append({
                    "nombre": str(nombre_val).strip(),
                    "codigo": str(codigo_val).strip(),
                    "stock": stock_val,
                    "stock_minimo": stock_min_val,
                    "precio": precio_val
                })

            if not lista_normalizada:
                return False, [], "La IA no logró detectar ningún producto legible en la foto.", False

            return True, lista_normalizada, f"Se detectaron {len(lista_normalizada)} producto(s) correctamente.", False
        
        return False, [], f"Error del servidor, por favor intenta nuevamente.", False

    except requests.exceptions.RequestException as e:
        return False, [], f"Error de conexión con n8n: {str(e)}", False
    except Exception as e:
        return False, [], f"Error al procesar la respuesta: {str(e)}", False


def enviar_datos_a_excel_n8n(productos: List[Dict[str, Any]]) -> Tuple[bool, str, bool]:
    
    if not productos:
        return False, "La tabla está vacía. No hay datos para enviar.", False

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
            return True, f"¡{len(productos)} registros enviados y organizados en Google Sheets con éxito!", False
        
        return False, f"Error en webhook de Google Sheets (HTTP {response.status_code}): {response.text[:150]}", False

    except requests.exceptions.RequestException as e:
        return False, f"Fallo al conectar con n8n Google Sheets: {str(e)}", False
    except Exception as e:
        return False, f"Error inesperado: {str(e)}", False
