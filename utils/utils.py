import streamlit as st

# Funciones auxiliares
def convertir_tea_a_periodica(tea, frecuencia):
    """Convierte TEA a tasa periódica"""
    periodos = {
        'Mensual': 30, 'Bimestral': 60, 'Trimestral': 90,
        'Cuatrimestral': 120, 'Semestral': 180, 'Anual': 360
    }
    n = periodos.get(frecuencia, 30)
    return (1 + tea/100)**(n / 360) - 1

def formato_moneda(valor):
    """Formatea valores en dólares"""
    return f"${valor:,.2f}"

def mostrar_ayuda(texto):
    """Muestra texto de ayuda"""
    return st.markdown(f'<p class="help-text">💡 {texto}</p>', unsafe_allow_html=True)