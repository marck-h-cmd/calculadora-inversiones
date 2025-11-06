import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils.utils import convertir_tea_a_periodica, formato_moneda, mostrar_ayuda
from ui.forms.form_mod_a import show_mod_a_form
from ui.forms.form_mod_b import show_mod_b_form
from ui.forms.form_mod_c import show_mod_c_form
from ui.components.sidebar import show_sidebar
from ui.components.footer import show_footer
# Configuración de la página
st.set_page_config(
    page_title="Simulador Financiero",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .help-text {
        font-size: 0.85em;
        color: #666;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("💰 Simulador Financiero Interactivo")
st.markdown("### Planifica tu futuro financiero con proyecciones precisas")


modulo = show_sidebar()


if modulo == "📈 Crecimiento de Cartera":
    # MÓDULO A: CRECIMIENTO DE CARTERA
    show_mod_a_form()

elif modulo == "🏦 Proyección de Retiro":
    # MÓDULO B: PROYECCIÓN DE RETIRO
    show_mod_b_form()

else:  # Valoración de Bonos
    # MÓDULO C: VALORACIÓN DE BONOS
    show_mod_c_form()


show_footer()