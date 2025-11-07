import streamlit as st

def show_footer():
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>Simulador Financiero Interactivo</strong></p>
            <p style='font-size: 0.85em;'>Todos los cálculos son estimados. Consulta con un asesor financiero para decisiones importantes.</p>
            <p style='font-size: 0.85em;'>💡 Los valores mostrados están en dólares estadounidenses (USD)</p>
        </div>
    """, unsafe_allow_html=True)