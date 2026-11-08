import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Cargar variables locales desde .env si existe
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

def get_secret(key: str, default: str = "") -> str:
    """
    Busca de manera segura una variable en:
    1. st.secrets (Nativo de Streamlit Cloud y .streamlit/secrets.toml)
    2. os.environ / archivo .env
    3. Valor por defecto proporcionado 
    """
    try:
        val = st.secrets.get(key)
        if val is not None:
            return str(val)
    except Exception:
        pass
    return os.getenv(key, default)

# URLs de los Webhooks de n8n
N8N_IMAGE_WEBHOOK_URL = get_secret("N8N_IMAGE_WEBHOOK_URL", "")
N8N_EXCEL_WEBHOOK_URL = get_secret("N8N_EXCEL_WEBHOOK_URL", "")
