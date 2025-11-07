from datetime import datetime
import google.generativeai as genai
import os
import streamlit as st

# Configurar Gemini
def configurar_gemini():
    """Configura la API de Gemini"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        if not api_key:
            st.error("🔑 API key de Gemini no encontrada. Configura la variable de entorno GEMINI_API_KEY")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model
    except Exception as e:
        st.error(f"❌ Error configurando Gemini: {e}")
        return None

# System prompt para inversiones (el que ya creamos)
investment_system_prompt = """
Eres un asesor financiero experto en planificación de jubilación y crecimiento de carteras. 
Analizarás los resultados de simulaciones de inversión y proporcionarás conclusiones y recomendaciones personalizadas.

**PARÁMETROS DE ENTRADA:**
- Edad Actual
- Monto Inicial (USD)
- Tipo de Impuesto: Bolsa Local (5%) o Bolsa Extranjera (29.5%)
- Aporte Periódico (USD)
- Tasa Efectiva Anual (%)
- Frecuencia de Aportes
- Tiempo de retiro (Plazo en años o Edad de Jubilación)
- Tipo de Retiro: Cobro total o Pensión Mensual

**RESULTADOS CALCULADOS:**
- Ingresos totales
- Costos totales (Capital invertido)
- Renta total (Ganancias)
- ROI (Return on Investment)
- Impuestos pagados
- Cobro total a retirar (Neto después de impuestos)

**ANÁLISIS REQUERIDO:**

1. **EVALUACIÓN DE RENTABILIDAD:**
   - Análisis del ROI (%): ¿Es adecuado para el plazo y riesgo?
   - Comparación con benchmarks del mercado
   - Eficiencia de la estrategia de aportes periódicos

2. **IMPACTO FISCAL:**
   - Evaluación de la carga impositiva vs. ganancias
   - Recomendaciones de optimización fiscal según tipo de impuesto
   - Análisis de eficiencia fiscal de la estrategia

3. **ANÁLISIS DE CRECIMIENTO:**
   - Relación entre aportes y crecimiento del capital
   - Efecto del interés compuesto en el tiempo
   - Sostenibilidad del plan de ahorro

4. **RECOMENDACIONES ESTRATÉGICAS:**
   - Ajustes en montos o frecuencia de aportes
   - Optimización del tipo de impuesto si es posible
   - Consideraciones sobre el tipo de retiro elegido

5. **EVALUACIÓN DE RIESGOS:**
   - Dependencia de la tasa de retorno
   - Riesgo de longevidad si es pensión mensual
   - Concentración de riesgo

**FORMATO DE RESPUESTA:**
- Conclusiones principales (3-4 puntos clave)
- Recomendaciones accionables específicas
- Advertencias sobre riesgos identificados
- Sugerencias de mejora con impacto cuantificable

Responde en español de manera profesional pero accesible.
"""

def generar_analisis_inversiones(datos_inversion):
    """Genera análisis de inversiones usando Gemini"""
    
    prompt = f"""
{investment_system_prompt}

**DATOS DEL CLIENTE A ANALIZAR:**

📋 PARÁMETROS INICIALES:
- Edad Actual: {datos_inversion['edad_actual']}
- Monto Inicial: ${datos_inversion['monto_inicial']:,.2f} USD
- Tipo de Impuesto: {datos_inversion['tipo_impuesto']}
- Aporte Periódico: ${datos_inversion['aporte_periodico']:,.2f} USD
- Frecuencia de Aportes: {datos_inversion['frecuencia_aportes']}
- TEA: {datos_inversion['tea']}%
- Tiempo de Retiro: {datos_inversion['tiempo_retiro']}
- Tipo de Retiro: {datos_inversion['tipo_retiro']}
{f"- TEA Durante Retiro: {datos_inversion['tea_retiro']}%" if datos_inversion.get('tea_retiro') else ""}

📊 RESULTADOS OBTENIDOS:
- 💰 Ingresos totales: ${datos_inversion['ingresos_totales']:,.2f}
- 💵 Costos totales (Capital invertido): ${datos_inversion['costos_totales']:,.2f}
- 📈 Renta total (Ganancias): ${datos_inversion['renta_total']:,.2f}
- 🎯 ROI: {datos_inversion['roi']}%
- 🏛️ Impuestos pagados: ${datos_inversion['impuestos']:,.2f}
{f"- 🏦 Cobro total a retirar: ${datos_inversion['cobro_total']:,.2f}" if datos_inversion.get('cobro_total') else f"- 💵 Pensión mensual estimada: ${datos_inversion['pension_mensual']:,.2f}"}
{f"- 📅 Cobro mensual bruto: ${datos_inversion['cobro_mensual_bruto']:,.2f}" if datos_inversion.get('cobro_mensual_bruto') else ""}

**SOLICITO ANÁLISIS COMPLETO:**
Proporciona un análisis profesional que incluya:
1. EVALUACIÓN GLOBAL de la estrategia de inversión
2. ANÁLISIS FISCAL detallado del impacto de impuestos
3. RECOMENDACIONES ESPECÍFICAS de mejora
4. ADVERTENCIAS sobre riesgos identificados
5. PROYECCIÓN de sostenibilidad a largo plazo
{f"6. ANÁLISIS DE SOSTENIBILIDAD de la pensión mensual" if datos_inversion.get('pension_mensual') else ""}
"""
    
    try:
        model = configurar_gemini()
        if not model:
            return "Error: No se pudo configurar Gemini"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar análisis: {str(e)}"
    
# System prompt para bonos (el que ya creamos)
bonds_system_prompt = """
Eres un analista especializado en valoración de instrumentos de renta fija. 
Analizarás la valoración de bonos y proporcionarás recomendaciones de inversión profesionales.

**PARÁMETROS DE ENTRADA:**
- Valor Nominal (USD)
- Tasa Cupón (% TEA)
- Frecuencia de Pago
- Plazo (Años)
- Tasa de Retorno Esperada (% TEA)

**RESULTADOS CALCULADOS:**
- Valor Presente del bono
- Valor Nominal
- Cupón Periódico
- Tipo de Bono (Descuento/Prima/Par)

**ANÁLISIS REQUERIDO:**

1. **VALORACIÓN RELATIVA:**
   - Análisis Precio/Valor Nominal
   - Determinación: Descuento, Prima o Par
   - Margen de seguridad del precio

2. **ANÁLISIS DE RENDIMIENTO:**
   - Tasa cupón vs. tasa de retorno esperada
   - Yield to Maturity (YTM) implícito
   - Rentabilidad real esperada

3. **ATRACTIVO DE INVERSIÓN:**
   - Evaluación del nivel de descuento/prima
   - Potencial de apreciación capital
   - Análisis riesgo/retorno

4. **SENSIBILIDAD Y RIESGO:**
   - Sensibilidad a cambios en tasas de interés
   - Duración implícita del bono
   - Riesgo de reinversión de cupones

5. **RECOMENDACIONES ESTRATÉGICAS:**
   - Decisión: Comprar/Mantener/Vender
   - Posicionamiento en cartera
   - Horizonte de inversión recomendado

**INDICADORES CLAVE A CONSIDERAR:**
- Spread sobre tasa de retorno
- Nivel de descuento/prima
- Perfil de flujos de caja
- Sensibilidad crediticia

**FORMATO DE RESPUESTA:**
- Calificación de atractivo (1-5 estrellas)
- Análisis técnico fundamentado
- Recomendación específica de acción
- Advertencias de riesgo relevantes

Responde en español de manera profesional pero accesible.
"""

def generar_analisis_bono(datos_bono):
    """Genera análisis de bonos usando Gemini"""
    
    # Determinar tipo de bono
    valor_presente = datos_bono['valor_presente']
    valor_nominal = datos_bono['valor_nominal']
    
    if valor_presente < valor_nominal:
        tipo_bono_detalle = f"Descuento (${valor_nominal - valor_presente:.2f} bajo par)"
    elif valor_presente > valor_nominal:
        tipo_bono_detalle = f"Prima (${valor_presente - valor_nominal:.2f} sobre par)"
    else:
        tipo_bono_detalle = "A la Par"
    
    prompt = f"""
{bonds_system_prompt}

**DATOS DEL BONO A ANALIZAR:**

📋 PARÁMETROS INICIALES:
- 💎 Valor Nominal: ${datos_bono['valor_nominal']:,.2f} USD
- 💰 Tasa Cupón: {datos_bono['tasa_cupon']}% TEA
- 📅 Frecuencia de Pago: {datos_bono['frecuencia_pago']}
- ⏱️ Plazo: {datos_bono['plazo']} años
- 📊 Tasa de Retorno Esperada: {datos_bono['tasa_retorno']}% TEA

📊 RESULTADOS DE VALORACIÓN:
- 💎 Valor Presente: ${datos_bono['valor_presente']:,.2f}
- 📄 Valor Nominal: ${datos_bono['valor_nominal']:,.2f}
- 💰 Cupón Periódico: ${datos_bono['cupon_periodico']:,.2f}
- 🔻 Tipo de Bono: {tipo_bono_detalle}

**MÉTRICAS CALCULADAS:**
- Diferencia Valor: ${datos_bono['valor_presente'] - datos_bono['valor_nominal']:+.2f}
- Porcentaje de Descuento/Prima: {((datos_bono['valor_presente'] / datos_bono['valor_nominal']) - 1) * 100:+.2f}%
- Spread vs Tasa Cupón: {datos_bono['tasa_retorno'] - datos_bono['tasa_cupon']:+.2f}%

**SOLICITO ANÁLISIS COMPLETO:**
Proporciona un análisis profesional que incluya:
1. EVALUACIÓN DEL ATRACTIVO del bono (1-5 estrellas)
2. ANÁLISIS TÉCNICO de la valoración actual
3. RECOMENDACIÓN ESPECÍFICA de inversión
4. ANÁLISIS DE SENSIBILIDAD a cambios de tasas
5. RIESGOS IDENTIFICADOS y consideraciones
"""
    
    try:
        model = configurar_gemini()
        if not model:
            return "Error: No se pudo configurar Gemini"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar análisis: {str(e)}"