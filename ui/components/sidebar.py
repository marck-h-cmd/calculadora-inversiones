import streamlit as st
from datetime import datetime

def show_sidebar():
    # Sidebar para navegación
   with st.sidebar:
    nombre = st.text_input("Ingrese su nombre")
    email = st.text_input("Ingrese su correo electrónico")
    
    # Guardar en session_state
    if 'email_destinatario' not in st.session_state:
        st.session_state.email_destinatario = ""
    if 'nombre_usuario' not in st.session_state:
        st.session_state.nombre_usuario = ""
    
    if email:
        st.session_state.email_destinatario = email
    if nombre:
        st.session_state.nombre_usuario = nombre

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

    return modulo,nombre,email