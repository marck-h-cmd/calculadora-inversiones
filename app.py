import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from utils.utils import convertir_tea_a_periodica, formato_moneda, mostrar_ayuda
from ui.forms.inversiones import show_inversiones
from ui.forms.bonos import show_bonos
from ui.components.sidebar import show_sidebar
from ui.components.footer import show_footer
import base64
import streamlit.components.v1 as components
import smtplib
import base64
import io
import resend
import os
from dotenv import load_dotenv
load_dotenv()

# Configuración de Resend
resend.api_key = os.getenv('EMAIL_API_KEY')



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
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("Simulador Financiero")
st.markdown("##### UNT - Finanzas Corporativas - Grupo 6")

modulo,nombre,email=show_sidebar()


if modulo == "📈 Inversiones":          # INVERSIONES
    # MÓDULO A: CRECIMIENTO DE CARTERA
    show_inversiones(nombre)

else:                                   # BONOS
    show_bonos(nombre)




show_footer()