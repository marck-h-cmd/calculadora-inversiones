import streamlit as st 
import pandas as pd
import numpy as np
from datetime import datetime
from utils.utils import convertir_tea_a_periodica, formato_moneda, mostrar_ayuda
from ui.forms.inversiones import show_inversiones
from ui.forms.bonos import show_bonos
from ui.components.sidebar import show_sidebar
from ui.components.footer import show_footer
import resend, os
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.getenv('EMAIL_API_KEY')

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador Financiero",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO GLOBAL Y SIDEBAR ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat+Alternates:wght@400;600;700&display=swap');

/* FONDO GENERAL CLARO */
body, .stApp {
    background-color: #f0f5f2;
    font-family: 'Montserrat Alternates', sans-serif;
    color: #0b2b1d;
}

/* SIDEBAR VERDE OSCURO */
[data-testid="stSidebar"] {
    background-color: #003d2f !important;
    color: #f5f5f5 !important;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] span {
    color: #f5f5f5 !important;
}
[data-testid="stSidebar"] .stButton>button {
    background: linear-gradient(90deg, #00796b, #004e40);
    color: #ffffff;
    font-weight: 600;
    border-radius: 6px;
    transition: all 0.3s ease-in-out;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background: linear-gradient(90deg, #004e40, #00796b);
    transform: scale(1.02);
}

    /* RADIO BUTTONS EN SIDEBAR - texto completamente blanco */
    [data-testid="stSidebar"] div[role="radiogroup"] label,
    [data-testid="stSidebar"] div[role="radiogroup"] label span,
    [data-testid="stSidebar"] div[role="radiogroup"] label div {
        color: #ffffff !important;  /* blanco total */
        font-weight: 600;
        font-size: 1rem;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover,
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover span,
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover div {
        color: #b2fff0 !important;  /* color al pasar el mouse */
    }

/* ENCABEZADO */
.header-container {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 2rem;
    padding: 2rem;
    margin-bottom: 1rem;
}
.header-text h1 {
    font-size: 2.8rem;
    font-weight: 800;
    color: #005b46;
    margin: 0;
}
.header-text .subtitle {
    font-size: 1.15rem;
    font-weight: 600;
    color: #2e4b44;
    margin: 0.2rem 0;
}
.header-text .tagline {
    font-size: 1rem;
    color: #3c5148;
    opacity: 0.85;
    margin: 0;
}
.header-image img {
    max-width: 120px;
}

/* DIVIDER PRINCIPAL Y FINAL */
.divider, .final-divider {
    height: 3px;
    background-color: #003d2f;
    border-radius: 2px;
    margin: 1.5rem 0 2rem 0;
    width: 100%;
}

/* OPCIONES PLANAS */
.option-card {
    flex: 1;
    min-width: 300px;
    background: #ffffff;
    border-radius: 14px;
    padding: 2rem 1.5rem;
    text-align: center;
    border: 2px solid #003d2f;
    color: #0b2b1d;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.option-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}
.option-card h3 {
    font-size: 1.4rem;
    font-weight: 700;
    color: #006f54;
    margin-bottom: 0.5rem;
}
.option-card p {
    font-size: 1rem;
    color: #2e453c;
    line-height: 1.5;
}

/* SECCIÓN DE MÓDULOS */
.section-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 2.5rem;
    margin-bottom: 3rem;
    border: 2px solid #003d2f;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}
.section-card h3 {
    font-size: 1.45rem;
    font-weight: 700;
    color: #006f54;
    margin-bottom: 0.6rem;
}
.section-desc {
    font-size: 1rem;
    color: #2e453c;
}
</style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
st.markdown("""
<div class="header-container">
  <div class="header-text">
    <h1>💰 Simulador Financiero</h1>
    <p class="subtitle"><b>UNT – Finanzas Corporativas · Grupo 6</b></p>
    <p class="tagline">Análisis financiero preciso y visual, orientado a la toma de decisiones estratégicas.</p>
  </div>
  <div class="header-image" style="margin-left:auto;">
    <img src="https://img.icons8.com/color/160/money-bag.png" alt="icono financiero">
  </div>
</div>

<div style="height:3px; background-color:#003d2f; border-radius:2px; margin:1.5rem 0 2rem 0; width:100%;"></div>
""", unsafe_allow_html=True)

# --- CONTENIDO PRINCIPAL ---
modulo, nombre, email = show_sidebar()

# --- OPCIONES ---
st.markdown("""
<div style="display:flex; justify-content:center; gap:2rem; flex-wrap:wrap; margin-bottom:3rem;">
  <div class="option-card">
    <h3>📈 Inversiones</h3>
    <p>Explora rendimientos, tasas y proyecciones.<br>
    Visualiza el crecimiento de tu capital de manera profesional y clara.</p>
  </div>
  <div class="option-card">
    <h3>📊 Bonos</h3>
    <p>Consulta precios, cupones y tasas de rendimiento.<br>
    Analiza escenarios financieros con criterios técnicos y confiables.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# --- MÓDULOS ---
if modulo == "📈 Inversiones":
    show_inversiones(nombre)
else:
    st.markdown("""
    """, unsafe_allow_html=True)
    show_bonos(nombre)


# --- FOOTER ---
show_footer()
