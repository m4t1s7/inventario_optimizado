# 📦 Smart Inventory AI Scanner (Streamlit + n8n)

Aplicación web modular construida con **Streamlit**, diseñada para capturar fotos de productos, procesarlas con IA mediante un webhook de **n8n**, consolidar los datos en una tabla interactiva editable y finalmente exportar el inventario a **Excel** a través de un segundo webhook de n8n.

---

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar tus Secretos (URLs de Webhooks)
Tus URLs están 100% protegidas mediante el archivo `.streamlit/secrets.toml` (o `.env`):

Abre `.streamlit/secrets.toml` y añade tus URLs reales de n8n:
```toml
N8N_IMAGE_WEBHOOK_URL = "https://tu-n8n.com/webhook/analizar-imagen"
N8N_EXCEL_WEBHOOK_URL = "https://tu-n8n.com/webhook/guardar-excel"
ENABLE_MOCK_FALLBACK = true
```

> **Nota:** Si dejas las URLs de ejemplo o vacías, la app entrará en **Modo Simulación**, permitiéndote probar la cámara, animaciones y edición de tabla sin que se rompa.

### 3. Ejecutar la aplicación
```bash
streamlit run app.py
```

---

## 🔗 Estructura de Datos para n8n

### Webhook 1: Análisis de Imagen
- **Método:** `POST` (multipart/form-data)
- **Archivo enviado:** `image` (JPEG)
- **Respuesta esperada de n8n (JSON):**
```json
[
  {
    "nombre": "Café Colombiano 500g",
    "codigo": "CAF-8921",
    "stock": 15
  }
]
```
*(También se acepta un solo objeto `{ "nombre": "...", "codigo": "...", "stock": 10 }`)*

### Webhook 2: Guardado en Excel
- **Método:** `POST` (application/json)
- **Cuerpo enviado por la app:**
```json
{
  "evento": "confirmacion_inventario",
  "total_items": 2,
  "productos": [
    {
      "nombre": "Café Colombiano 500g",
      "codigo": "CAF-8921",
      "stock": 15
    },
    {
      "nombre": "Galletas de Avena 250g",
      "codigo": "GAL-4410",
      "stock": 30
    }
  ]
}
```

---

## 📁 Arquitectura Modular
- `app.py`: Punto de entrada principal y orquestador del dashboard.
- `config.py`: Gestor centralizado de secretos (`st.secrets` y `.env`).
- `services/n8n_service.py`: Lógica pura de peticiones HTTP a n8n y fallback de simulación.
- `components/camera_section.py`: Módulo de la cámara y carga de imágenes.
- `components/table_section.py`: Tabla editable (`st.data_editor`), métricas y botón de confirmación.
- `styles/custom_css.py`: Estilos visuales con micro-interacciones hover y sombras suaves.
