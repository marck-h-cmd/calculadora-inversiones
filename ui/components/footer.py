import streamlit as st

def show_footer():
    st.markdown("""
    <style>
    /* --- FOOTER SIMPLE Y FORMAL --- */
    .footer-container {
        text-align: center;
        color: #0b2b1d;
        padding: 1rem 0.5rem;
        border-top: 1px solid #004e40;
        background-color: #f0f5f2;
        font-family: 'Montserrat Alternates', sans-serif;
        font-size: 0.85rem;
        margin-top: 2rem;
    }

    .footer-container strong {
        color: #004e40;
        font-weight: 600;
    }

    .footer-container p {
        margin: 0.2rem 0;
        opacity: 0.8;
    }
    </style>

    <div class='footer-container'>
        <p><strong>💰 Simulador Financiero</strong></p>
        <p>Todos los cálculos son estimados. Consulta con un asesor financiero antes de tomar decisiones importantes.</p>
        <p>💡 Valores expresados en dólares estadounidenses (USD)</p>
        <p style='font-size:0.75rem; opacity:0.7;'>Creado por el equipo UNT - Grupo 6</p>
    </div>
    """, unsafe_allow_html=True)
