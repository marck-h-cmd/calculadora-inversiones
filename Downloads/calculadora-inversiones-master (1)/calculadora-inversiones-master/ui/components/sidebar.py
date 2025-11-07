import streamlit as st
from datetime import datetime

def show_sidebar():
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("""
        <style>
        /* --- CONTENEDOR SIDEBAR --- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b2f3a, #164a54);
            color: #f4f7f6 !important;
            border-right: 2px solid #d1e0dc;
            padding: 1rem !important;
        }

        /* --- TÍTULO PRINCIPAL --- */
        .sidebar-title {
            text-align: center;
            font-weight: 700;
            font-size: 1.3rem;
            color: #e8f9f5;
            margin-bottom: 1.3rem;
            font-family: 'Segoe UI', sans-serif;
            letter-spacing: 0.5px;
        }

        /* --- BLOQUE DE BIENVENIDA --- */
        .sidebar-welcome {
            background: #134247;
            border: 1px solid rgba(200,220,215,0.3);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            font-size: 0.95rem;
            color: #e3f4f1;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }

        /* --- INPUTS --- */
        input {
            background-color: #f8f9f9 !important;
            border: 1.5px solid #c5d6d2 !important;
            border-radius: 8px !important;
            color: #0b2f3a !important;
            font-weight: 500;
        }
        input:focus {
            border: 1.5px solid #009879 !important;
            box-shadow: 0 0 4px rgba(0,152,121,0.3);
        }

        /* --- RADIO BUTTONS --- */
        div[role="radiogroup"] label {
            color: #ffffff !important;  
            font-weight: 600;
        }
        div[role="radiogroup"] label:hover {
            color: #7be0c3 !important;  
        }


        /* --- DIVIDER --- */
        hr {
            border: 0;
            border-top: 1px solid #88c3b3;
            margin: 1.2rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

        # --- TÍTULO ---
        st.markdown("<div class='sidebar-title'>Panel de Usuario</div>", unsafe_allow_html=True)

        # --- CAMPOS DE ENTRADA ---
        nombre = st.text_input("👤 Nombre completo")
        email = st.text_input("📧 Correo electrónico")

        # --- GUARDAR EN SESSION_STATE ---
        if 'email_destinatario' not in st.session_state:
            st.session_state.email_destinatario = ""
        if 'nombre_usuario' not in st.session_state:
            st.session_state.nombre_usuario = ""

        if email:
            st.session_state.email_destinatario = email
        if nombre:
            st.session_state.nombre_usuario = nombre

        st.divider()

        # --- MENSAJE DE BIENVENIDA ---
        nombre_mostrar = nombre if nombre else "Usuario"
        st.markdown(
            f"<div class='sidebar-welcome'><b>Bienvenido(a), {nombre_mostrar}</b><br><span style='font-size:0.9rem;'>Seleccione el módulo que desea utilizar:</span></div>",
            unsafe_allow_html=True
        )

        # --- SELECCIÓN DE MÓDULO ---
        modulo = st.radio(
            "Seleccione un módulo:",
            ["📈 Inversiones", "📊 Bonos"]
        )

        return modulo, nombre, email

