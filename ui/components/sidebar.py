import streamlit as st
from datetime import datetime

def show_sidebar():
    # Sidebar para navegación
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/calculator.png", width=80)
        st.title("Navegación")
        
        modulo = st.radio(
            "Selecciona un módulo:",
            ["📈 Inversiones", "📊 Bonos"],
            label_visibility="collapsed"
        )
        
        st.divider()
        st.markdown("**Fecha:** " + datetime.now().strftime("%d/%m/%Y"))
        st.markdown("**Sistema:** Simulador Financiero v2")

    return modulo