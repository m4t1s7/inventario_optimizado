import streamlit as st

def load_custom_css():
    """
    Inyecta estilos CSS modernos para elevar el diseño de Streamlit,
    añadiendo micro-interacciones en botones, bordes suaves y tarjetas visuales.
    """
    custom_css = """
    <style>
    /* Tipografía y espaciado general */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Reducir padding superior excesivo de Streamlit */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 95% !important;
    }

    /* Tarjetas contenedoras limpias con sombras suaves */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.02) !important;
        padding: 18px !important;
        transition: all 0.25s ease-in-out !important;
    }

    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #CBD5E1 !important;
        box-shadow: 0 10px 24px -4px rgba(15, 23, 42, 0.08) !important;
    }

    /* Micro-interacciones para botones primarios */
    button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.65rem 1.4rem !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.38) !important;
        background: linear-gradient(135deg, #4338CA 0%, #3730A3 100%) !important;
    }

    button[kind="primary"]:active {
        transform: translateY(0px) scale(0.98) !important;
    }

    /* Micro-interacciones para botones secundarios */
    button[kind="secondary"] {
        border-radius: 12px !important;
        border: 1.5px solid #E2E8F0 !important;
        background: #F8FAFC !important;
        color: #334155 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    button[kind="secondary"]:hover {
        background: #F1F5F9 !important;
        border-color: #94A3B8 !important;
        color: #0F172A !important;
        transform: translateY(-2px) scale(1.01) !important;
    }

    button[kind="secondary"]:active {
        transform: translateY(0px) scale(0.98) !important;
    }

    /* Métricas estilizadas */
    div[data-testid="stMetric"] {
        background: #F8FAFC;
        border-radius: 12px;
        padding: 12px 18px;
        border: 1px solid #E2E8F0;
        transition: all 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        background: #F1F5F9;
        border-color: #CBD5E1;
    }

    div[data-testid="stMetricLabel"] p {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }

    /* Insignias de estado (Badge) */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .badge-live {
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #BBF7D0;
    }

    .badge-demo {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
    }

    .pulsing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: currentColor;
        animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.25); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* Encabezados y títulos modernos */
    .header-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #0F172A;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .header-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 1.2rem;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
