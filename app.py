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

with st.sidebar:
  nombre = st.text_input("Ingrese su nombre")
  email = st.text_input("Ingrese su correo electrónico")
  if st.button("Enviar a mi correo"):
    if email:
        html_code = f"""
        <script src="https://cdn.emailjs.com/dist/email.min.js"></script>
        <script>
          (function(){{
            emailjs.init(" "); // tu Public Key

            emailjs.send(
              " ", // service key
              " ", // template key
              {{
                to_name: "{nombre}",
                to_email: "{email}",
                message: "Este es un mensaje de prueba",
                extra_summary: "Resumen de prueba"
              }}
            ).then(function(response){{
              alert("✅ Correo enviado!");
              console.log(response);
            }}, function(error){{
              alert("❌ Error al enviar: " + JSON.stringify(error));
              console.log(error);
            }});
          }})();
        </script>
        """
        components.html(html_code, height=0)
        st.success("Intentando enviar correo, revisa tu bandeja de entrada.")
    else:
        st.warning("⚠️ Ingresa un correo válido primero.")

  st.divider()

  if nombre:
      st.markdown(f"<h3>Bienvenido(a) <b>{nombre}</b>. ¿Qué desea hacer hoy?</h3>", unsafe_allow_html=True)
  else:
      nombre = "Usuario"
      st.markdown(f"<h3>Bienvenido(a) <b>{nombre}</b>. ¿Qué desea hacer hoy?</h3>", unsafe_allow_html=True)

  modulo = st.radio(
      "Seleccione un modo:",
      ["📈 Inversiones", "📊 Bonos"]
  )



if modulo == "📈 Inversiones":          # INVERSIONES
    # MÓDULO A: CRECIMIENTO DE CARTERA
    show_inversiones(nombre)

else:                                   # BONOS
    show_bonos(nombre)




show_footer()