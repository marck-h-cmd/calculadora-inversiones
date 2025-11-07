from utils.utils import convertir_tea_a_periodica, formato_moneda, mostrar_ayuda
from ui.results.res_mod_c import (
    mostrar_resultados_completos,
    comparacion_escenarios,
    grafico_sensibilidad
)
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import plotly.io as pio
from utils.email import crear_template_email, enviar_email_con_pdf_gmail



def guardar_grafico_como_imagen(fig):
    """Función eliminada ya que no usamos gráficos en PDF"""
    pass

def generar_pdf_bonos(valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono,
                      tea_bono, df_flujos, valor_presente_total, cupon,
                      tasa_cupon_periodica, tasa_descuento_periodica):
    """Genera un PDF profesional SIN GRÁFICOS con el reporte de valoración del bono"""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    story = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8
    )

    # Título principal
    story.append(Paragraph("REPORTE DE VALORACIÓN DE BONOS", title_style))
    story.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 0.3 * inch))

    # Sección 1: Parámetros del Bono
    story.append(Paragraph("1. PARÁMETROS DEL BONO", subtitle_style))

    parametros_data = [
        ['Parámetro', 'Valor'],
        ['Valor Nominal', formato_moneda(valor_nominal)],
        ['Tasa Cupón (TEA)', f"{tasa_cupon}%"],
        ['Tasa Cupón Periódica', f"{tasa_cupon_periodica * 100:.4f}%"],
        ['Frecuencia de Pago', frecuencia_bono],
        ['Plazo', f"{plazo_bono} años"],
        ['Tasa de Descuento (TEA)', f"{tea_bono}%"],
        ['Tasa de Descuento Periódica', f"{tasa_descuento_periodica * 100:.4f}%"],
        ['Cupón por Período', formato_moneda(cupon)]
    ]

    tabla_parametros = Table(parametros_data, colWidths=[3 * inch, 2 * inch])
    tabla_parametros.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    story.append(tabla_parametros)
    story.append(Spacer(1, 0.3 * inch))

    # Sección 2: Resumen de Valoración
    story.append(Paragraph("2. RESUMEN DE VALORACIÓN", subtitle_style))

    periodos_bono = {
        'Mensual': 12, 'Bimestral': 6, 'Trimestral': 4,
        'Cuatrimestral': 3, 'Semestral': 2, 'Anual': 1
    }
    total_periodos = plazo_bono * periodos_bono[frecuencia_bono]

    # Calcular diferencia y tipo de bono
    diferencia = valor_presente_total - valor_nominal

    if diferencia > 0:
        tipo_bono = "Premium (Sobre Par)"
        interpretacion = f"El bono cotiza con prima. Su valor presente es {formato_moneda(diferencia)} mayor que el valor nominal."
    elif diferencia < 0:
        tipo_bono = "Descuento (Bajo Par)"
        interpretacion = f"El bono cotiza con descuento. Su valor presente es {formato_moneda(abs(diferencia))} menor que el valor nominal."
    else:
        tipo_bono = "A la Par"
        interpretacion = "El bono cotiza a la par. Su valor presente es igual al valor nominal."

    resumen_data = [
        ['Métrica', 'Valor'],
        ['Número Total de Períodos', str(total_periodos)],
        ['Valor Presente del Bono', formato_moneda(valor_presente_total)],
        ['Valor Nominal', formato_moneda(valor_nominal)],
        ['Diferencia (VP - VN)', formato_moneda(diferencia)],
        ['Tipo de Bono', tipo_bono]
    ]

    tabla_resumen = Table(resumen_data, colWidths=[3 * inch, 2 * inch])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    story.append(tabla_resumen)
    story.append(Spacer(1, 0.2 * inch))

    # Interpretación
    interpretacion_para = Paragraph(f"<b>Interpretación:</b> {interpretacion}", normal_style)
    story.append(interpretacion_para)
    story.append(Spacer(1, 0.3 * inch))

    # Sección 3: Análisis de Resultados (REEMPLAZA LOS GRÁFICOS)
    story.append(Paragraph("3. ANÁLISIS DE RESULTADOS", subtitle_style))

    # Análisis textual en lugar de gráficos
    analisis_texto = [
        f"• <b>Valoración:</b> El bono tiene un valor presente de {formato_moneda(valor_presente_total)}",
        f"• <b>Comparación con valor nominal:</b> {formato_moneda(diferencia)} ({tipo_bono})",
        f"• <b>Rentabilidad:</b> La tasa cupón del {tasa_cupon}% se compara con la tasa de descuento del {tea_bono}%",
        f"• <b>Flujos totales:</b> {total_periodos} pagos periódicos durante {plazo_bono} años",
        f"• <b>Frecuencia:</b> Pagos {frecuencia_bono.lower()} con cupones de {formato_moneda(cupon)}"
    ]

    for item in analisis_texto:
        story.append(Paragraph(item, normal_style))

    story.append(Spacer(1, 0.3 * inch))

    # Sección 4: Detalle Completo de Flujos
    story.append(Paragraph("4. DETALLE COMPLETO DE FLUJOS DE CAJA", subtitle_style))

    # Preparar datos de la tabla
    flujos_data = [['Período', 'Año', 'Flujo de Caja', 'Valor Presente']]

    # Filtrar solo filas que no son totales
    df_flujos_normales = df_flujos[df_flujos['Es_Total'] == False]

    for _, row in df_flujos_normales.iterrows():
        flujos_data.append([
            str(row['Periodo']),
            f"{row['Año']:.2f}" if pd.notna(row['Año']) else '',
            formato_moneda(row['Flujo']) if pd.notna(row['Flujo']) else '',
            formato_moneda(row['Valor Presente'])
        ])

    # Agregar fila de totales de forma segura
    fila_total_df = df_flujos[df_flujos['Es_Total'] == True]
    if not fila_total_df.empty:
        fila_total = fila_total_df.iloc[0]
        flujos_data.append([
            'TOTAL',
            '',
            '',
            formato_moneda(fila_total['Valor Presente'])
        ])

    tabla_flujos = Table(flujos_data, colWidths=[1 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    tabla_flujos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    story.append(tabla_flujos)

    # Nota explicativa
    nota = Paragraph(
        "<i>Nota: Período 0 representa el momento inicial de la inversión. "
        "La fila TOTAL muestra el valor presente total de todos los flujos.</i>",
        normal_style
    )
    story.append(Spacer(1, 0.1 * inch))
    story.append(nota)

    # Sección 5: Recomendaciones
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("5. RECOMENDACIONES", subtitle_style))

    if diferencia > 0:
        recomendaciones = [
            "✓ El bono es atractivo para compra (cotiza con prima)",
            "✓ La tasa cupón es mayor que el rendimiento requerido",
            "✓ Considerar mantener hasta el vencimiento"
        ]
    elif diferencia < 0:
        recomendaciones = [
            "✓ El bono puede ser una oportunidad de compra (cotiza con descuento)",
            "✓ La tasa cupón es menor que el rendimiento requerido",
            "✓ Posible ganancia de capital si las tasas disminuyen"
        ]
    else:
        recomendaciones = [
            "✓ El bono cotiza a su valor justo",
            "✓ Rentabilidad equivalente al rendimiento requerido",
            "✓ Decisión neutral de compra/venta"
        ]

    for rec in recomendaciones:
        story.append(Paragraph(rec, normal_style))

    # Pie de página
    story.append(Spacer(1, 0.5 * inch))
    footer = Paragraph(
        "Este reporte ha sido generado automáticamente por el Sistema de Valoración de Bonos<br/>"
        "© 2025 - Calculadora de Inversiones Financieras",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    story.append(footer)

    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def calcular_valoracion_bono(valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono, tea_bono):
    """Función para calcular la valoración del bono con período 0 = Año 1"""
    periodos_bono = {
        'Mensual': 12, 'Bimestral': 6, 'Trimestral': 4,
        'Cuatrimestral': 3, 'Semestral': 2, 'Anual': 1
    }

    num_periodos_bono = periodos_bono[frecuencia_bono]
    total_periodos_bono = plazo_bono * num_periodos_bono

    tasa_cupon_periodica = convertir_tea_a_periodica(tasa_cupon, frecuencia_bono)
    tasa_descuento_periodica = convertir_tea_a_periodica(tea_bono, frecuencia_bono)

    cupon = valor_nominal * tasa_cupon_periodica

    # Calcular flujos y valor presente
    flujos = []
    valor_presente_total = 0

    # Períodos 0 a n-1 (flujos normales)
    for i in range(total_periodos_bono):
        if i == total_periodos_bono - 1:  # Último período
            flujo = cupon + valor_nominal  # Cupón + principal
        else:
            flujo = cupon  # Períodos intermedios: solo cupón

        # El período i corresponde al año (i + 1) / num_periodos_bono
        año = (i + 1) / num_periodos_bono
        vp = flujo / ((1 + tasa_descuento_periodica) ** (i + 1))
        valor_presente_total += vp

        flujos.append({
            'Periodo': i,  # 0, 1, 2, ..., 14
            'Año': round(año, 2),
            'Flujo': flujo,
            'Valor Presente': vp,
            'Es_Total': False
        })

    # FILA FINAL - Solo con el total del valor presente
    # Usar NaN para mantener el tipo numérico de la columna Año
    flujos.append({
        'Periodo': total_periodos_bono,  # 15
        'Año': float('nan'),  # Usar NaN en lugar de string
        'Flujo': float('nan'),  # Usar NaN en lugar de string
        'Valor Presente': valor_presente_total,
        'Es_Total': True
    })

    df_flujos = pd.DataFrame(flujos)

    return {
        'df_flujos': df_flujos,
        'valor_presente_total': valor_presente_total,
        'cupon': cupon,
        'tasa_cupon_periodica': tasa_cupon_periodica,
        'tasa_descuento_periodica': tasa_descuento_periodica,
        'num_periodos_bono': num_periodos_bono,
        'total_periodos_bono': total_periodos_bono
    }


def show_bonos(nombre):
    st.header("📊 Módulo C: Valoración de Bonos")
    st.markdown("Calcula el valor presente de un bono según sus características y pagos periódicos.")

    # SECCIÓN DE EJEMPLO EDUCATIVO
    with st.expander("Ejemplo Práctico: Evaluación de Cartera de Bonos", expanded=False):
        st.markdown("""
        ### 🎓 Guía de Evaluación de Bonos

        **Objetivo:** Aprender a comparar múltiples bonos para tomar decisiones de inversión informadas.

        #### 📖 Conceptos Fundamentales

        **Características principales de un Bono:**

        1. **💎 Valor Nominal (VN):** Es el valor facial del bono, la cantidad que el emisor se 
           compromete a pagar al tenedor al vencimiento. También llamado "valor par".

        2. **💰 Cupón (Tasa Cupón TEA):** Es la tasa de interés anual que el bono paga sobre su 
           valor nominal. Por ejemplo, un bono de S/1,000 con cupón del 8% paga S/80 anuales.

        3. **⏱️ Plazo:** Tiempo hasta el vencimiento del bono, expresado en años. Define cuándo 
           se devolverá el valor nominal y cuántos pagos de cupón se recibirán.

        4. **📅 Frecuencia de Pago:** Indica cada cuánto tiempo se pagan los cupones 
           (mensual, trimestral, semestral, anual, etc.). Afecta el flujo de caja del inversor.

        5. **📊 Rendimiento Requerido (Tasa de Descuento):** Es la tasa de retorno que el 
           inversor exige para comprar el bono, basada en el riesgo y alternativas del mercado.

        **Tipos de Valoración:**

        - **🔺 Bono con Prima (Sobre Par):** VP > VN  
          Ocurre cuando la tasa cupón es mayor que el rendimiento requerido.  
          El bono es atractivo porque paga más que las alternativas del mercado.

        - **🔻 Bono con Descuento (Bajo Par):** VP < VN  
          Ocurre cuando la tasa cupón es menor que el rendimiento requerido.  
          El bono debe venderse más barato para compensar su menor tasa de interés.

        - **➖ Bono a la Par:** VP = VN  
          Ocurre cuando la tasa cupón iguala el rendimiento requerido del mercado.

        ---

        #### 🔍 Ejemplo Práctico
        Este ejercicio muestra cómo evaluar una cartera de 3 bonos corporativos diferentes,
        comparando sus características y determinando cuál ofrece mejor valor.
        """)

        st.divider()
        st.subheader("🔍 Comparación de Bonos Corporativos")

        # (Tu código existente del ejemplo aquí)

    # SECCIÓN PRINCIPAL: VALORACIÓN INDIVIDUAL
    st.divider()
    st.subheader("⚙️ Valoración Individual de Bono")

    # Formulario de inputs
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            valor_nominal = st.number_input(
                "💎 Valor Nominal (USD)",
                min_value=100.0, value=1000.0, step=100.0,
                help="Valor que recibirás al vencimiento del bono"
            )

            tasa_cupon = st.number_input(
                "💰 Tasa Cupón (% TEA)",
                min_value=0.0, max_value=50.0, value=6.0, step=0.1,
                help="Tasa de interés que paga el bono anualmente"
            )

        with col2:
            frecuencia_bono = st.selectbox(
                "📅 Frecuencia de Pago",
                ['Mensual', 'Bimestral', 'Trimestral', 'Cuatrimestral', 'Semestral', 'Anual'],
                index=4,
                help="Cada cuánto tiempo recibirás los cupones"
            )

            plazo_bono = st.number_input(
                "⏱️ Plazo (Años)",
                min_value=1, max_value=50, value=5, step=1,
                help="Años hasta el vencimiento del bono"
            )

        with col3:
            tea_bono = st.number_input(
                "📊 Tasa de Retorno Esperada (% TEA)",
                min_value=0.0, max_value=50.0, value=7.0, step=0.1,
                help="Tasa de descuento para calcular el valor presente"
            )

    # CÁLCULOS
    st.divider()

    resultados = calcular_valoracion_bono(
        valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono, tea_bono
    )

    # MOSTRAR RESULTADOS CON LEYENDAS MEJORADAS
    total_periodos = mostrar_resultados_completos(
        valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono,
        tea_bono, resultados['df_flujos'], resultados['valor_presente_total'],
        resultados['cupon'], resultados['tasa_cupon_periodica'],
        resultados['tasa_descuento_periodica'], resultados['num_periodos_bono']
    )

    # PREPARAR DATOS PARA GRÁFICOS
    df_para_graficos = resultados['df_flujos'][resultados['df_flujos']['Es_Total'] == False].copy()

    # GRÁFICO 1: FLUJOS DE CAJA
    st.subheader("💵 Flujos de Caja vs Valor Presente")

    fig_flujos = go.Figure()
    fig_flujos.add_trace(go.Bar(
        x=df_para_graficos['Año'],
        y=df_para_graficos['Flujo'],
        name='Flujo de Caja Nominal',
        marker_color='#3B82F6',
        hovertemplate='<b>Año:</b> %{x:.2f}<br><b>Flujo:</b> $%{y:,.2f}<extra></extra>'
    ))
    fig_flujos.add_trace(go.Bar(
        x=df_para_graficos['Año'],
        y=df_para_graficos['Valor Presente'],
        name='Valor Presente Descontado',
        marker_color='#10B981',
        hovertemplate='<b>Año:</b> %{x:.2f}<br><b>VP:</b> $%{y:,.2f}<extra></extra>'
    ))

    fig_flujos.update_layout(
        title={
            'text': 'Flujos de Caja vs Valor Presente por Período',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Año",
        yaxis_title="Valor (USD)",
        barmode='group',
        height=450,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig_flujos, use_container_width=True, key="grafico_flujos_bonos")
    st.caption("📊 **Leyenda:** Las barras azules muestran los flujos nominales (cupones + valor nominal al final). "
               "Las barras verdes representan el valor presente de cada flujo descontado a la tasa requerida. "
               "La diferencia ilustra el efecto del valor del dinero en el tiempo.")

    # GRÁFICO 2: VALOR PRESENTE ACUMULADO
    st.subheader("📈 Valor Presente Acumulado")

    df_temp = df_para_graficos.copy()
    df_temp['VP Acumulado'] = df_temp['Valor Presente'].cumsum()

    fig_acumulado = go.Figure()

    # Línea principal de VP Acumulado
    fig_acumulado.add_trace(go.Scatter(
        x=df_temp['Año'],
        y=df_temp['VP Acumulado'],
        mode='lines+markers',
        name='VP Acumulado',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.2)',
        hovertemplate='<b>Año:</b> %{x:.2f}<br><b>VP Acum:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    # Línea de referencia del Valor Nominal
    fig_acumulado.add_trace(go.Scatter(
        x=[df_temp['Año'].min(), df_temp['Año'].max()],
        y=[valor_nominal, valor_nominal],
        mode='lines',
        name='Valor Nominal',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='<b>Valor Nominal:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    fig_acumulado.update_layout(
        title={
            'text': 'Evolución del Valor Presente Acumulado',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Año",
        yaxis_title="Valor (USD)",
        height=450,
        template='plotly_white',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.2)',
            borderwidth=1
        )
    )

    st.plotly_chart(fig_acumulado, use_container_width=True, key="grafico_acumulado_bonos")
    st.caption("📈 **Leyenda:** La línea morada muestra cómo se acumula el valor presente de los flujos. "
               "La línea roja punteada es el valor nominal. Cuando se cruzan, los flujos futuros descontados "
               "igualan el valor nominal del bono.")

    # ANÁLISIS DE SENSIBILIDAD
    st.divider()
    st.subheader("📉 Análisis de Sensibilidad a Tasas de Interés")

    # Generar datos para el gráfico de sensibilidad
    tasas_rango = [i / 10 for i in range(10, 201, 5)]  # 1% a 20%
    valores_sensibilidad = []

    for tasa in tasas_rango:
        tasa_per = convertir_tea_a_periodica(tasa, frecuencia_bono)
        vp = sum([
            (resultados['cupon'] if i < resultados['total_periodos_bono'] else resultados['cupon'] + valor_nominal) /
            ((1 + tasa_per) ** i)
            for i in range(1, resultados['total_periodos_bono'] + 1)
        ])
        valores_sensibilidad.append(vp)

    fig_sensibilidad = go.Figure()

    # Línea principal del valor del bono
    fig_sensibilidad.add_trace(go.Scatter(
        x=tasas_rango,
        y=valores_sensibilidad,
        mode='lines',
        name='Valor del Bono',
        line=dict(color='#6366f1', width=3),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.2)',
        hovertemplate='<b>Tasa:</b> %{x:.2f}%<br><b>Valor:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    # Línea de referencia del Valor Nominal
    fig_sensibilidad.add_trace(go.Scatter(
        x=[min(tasas_rango), max(tasas_rango)],
        y=[valor_nominal, valor_nominal],
        mode='lines',
        name='Valor Nominal (Par)',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='<b>Valor Nominal:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    # Línea de referencia de la Tasa Actual
    fig_sensibilidad.add_trace(go.Scatter(
        x=[tea_bono, tea_bono],
        y=[min(valores_sensibilidad), max(valores_sensibilidad)],
        mode='lines',
        name=f'Tasa Actual ({tea_bono}%)',
        line=dict(color='green', width=2, dash='dot'),
        hovertemplate='<b>Tasa Actual:</b> %{x:.2f}%<extra></extra>',
        showlegend=True
    ))

    # Punto actual
    valor_actual = resultados['valor_presente_total']
    fig_sensibilidad.add_trace(go.Scatter(
        x=[tea_bono],
        y=[valor_actual],
        mode='markers',
        name='Punto Actual',
        marker=dict(color='orange', size=12, symbol='star'),
        hovertemplate='<b>Tasa:</b> %{x:.2f}%<br><b>Valor:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    fig_sensibilidad.update_layout(
        title={
            'text': 'Sensibilidad del Valor del Bono ante Cambios en la Tasa de Descuento',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Tasa de Descuento (%)",
        yaxis_title="Valor del Bono (USD)",
        height=500,
        template='plotly_white',
        hovermode='closest',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(0, 0, 0, 0.3)',
            borderwidth=1
        )
    )

    st.plotly_chart(fig_sensibilidad, use_container_width=True, key="grafico_sensibilidad_bonos")
    st.caption("📉 **Leyenda:** Este gráfico demuestra la relación inversa entre tasa de descuento y valor del bono. "
               "A medida que aumenta el rendimiento requerido (eje X), el valor presente del bono disminuye (eje Y). "
               "La línea verde vertical marca tu tasa actual, y la línea roja horizontal el valor nominal.")

    # COMPARACIÓN DE ESCENARIOS
    with st.expander("🔄 Comparar con diferentes tasas", expanded=False):
        col_comp1, col_comp2 = st.columns(2)

        with col_comp1:
            tasa_escenario1 = st.number_input(
                "Escenario Optimista - Tasa (%)",
                min_value=0.0,
                max_value=50.0,
                value=tea_bono - 2.0 if tea_bono > 2.0 else 1.0,
                step=0.1,
                key="tasa_esc1_bonos"
            )

        with col_comp2:
            tasa_escenario2 = st.number_input(
                "Escenario Pesimista - Tasa (%)",
                min_value=0.0,
                max_value=50.0,
                value=tea_bono + 2.0,
                step=0.1,
                key="tasa_esc2_bonos"
            )

        # Mostrar comparación
        comparacion_escenarios(
            tasa_escenario1, tasa_escenario2, tea_bono,
            valor_nominal, resultados['cupon'], resultados['total_periodos_bono'],
            frecuencia_bono, convertir_tea_a_periodica
        )

        st.caption("💡 **Interpretación:** Los escenarios muestran cómo cambiaría el valor del bono "
                   "si las condiciones del mercado mejoran (tasa baja) o empeoran (tasa alta). "
                   "Esto te ayuda a evaluar el riesgo de tasa de interés.")

    # SECCIÓN: EXPORTACIÓN
    st.divider()

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        # Descarga CSV
        csv = resultados['df_flujos'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Flujos (CSV)",
            data=csv,
            file_name=f"valoracion_bono_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="descargar_csv_bonos"
        )

    with col_btn2:
        try:
            # Generar PDF SIN gráficos
            pdf_buffer = generar_pdf_bonos(
                valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono,
                tea_bono, resultados['df_flujos'], resultados['valor_presente_total'],
                resultados['cupon'], resultados['tasa_cupon_periodica'],
                resultados['tasa_descuento_periodica']
            )

            st.download_button(
                label="📄 Descargar PDF Reporte",
                data=pdf_buffer,
                file_name=f"reporte_bono_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="descargar_pdf_bonos"
            )

        except Exception as e:
            st.error(f"❌ Error al generar PDF: {str(e)}")
            st.info("💡 El PDF contiene análisis detallado y tablas completas")

    with col_btn3:
        if st.button("📧 Enviar por Email", use_container_width=True, key="email_bonos"):
            email_dest = st.session_state.get('email_destinatario')
            nombre_dest = st.session_state.get('nombre_usuario', 'Usuario')
            if nombre_dest == "":
                nombre_dest = "Usuario"

            if email_dest:
                # Preparar métricas para el email
                diferencia = resultados['valor_presente_total'] - valor_nominal
                tipo_bono = "Premium" if diferencia > 0 else "Descuento" if diferencia < 0 else "A la Par"

                metricas = {
                    "Valor Presente del Bono: ": formato_moneda(resultados['valor_presente_total']),
                    "Valor Nominal: ": formato_moneda(valor_nominal),
                    "Tipo de Bono: ": tipo_bono,
                    "Tasa Cupón: ": f"{tasa_cupon}%",
                    "Plazo: ": f"{plazo_bono} años",
                    "Frecuencia de Pago: ": frecuencia_bono
                }

                # Crear copia del buffer
                pdf_buffer_email = io.BytesIO(pdf_buffer.getvalue())

                with st.spinner("📤 Enviando reporte..."):
                    exito, resultado = enviar_email_con_pdf_gmail(
                        email_dest,
                        nombre_dest,
                        pdf_buffer_email,
                        "Valoración de Bonos",
                        metricas
                    )

                    if exito:
                        st.success(f"✅ Reporte enviado exitosamente a **{email_dest}**")
                    else:
                        st.error(f"❌ Error al enviar: {resultado}")
            else:
                st.warning("⚠️ Por favor ingresa tu correo en el panel lateral")