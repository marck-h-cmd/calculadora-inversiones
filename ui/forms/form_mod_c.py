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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io


def generar_pdf_bonos(valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono,
                      tea_bono, df_flujos, valor_presente_total, cupon,
                      tasa_cupon_periodica, tasa_descuento_periodica):
    """Genera un PDF profesional con el reporte de valoración del bono"""

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
    total_flujos = df_flujos['Flujo'].sum()
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
        ['Total de Flujos de Caja', formato_moneda(total_flujos)],
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

    # Sección 3: Detalle de Flujos
    story.append(Paragraph("3. DETALLE DE FLUJOS DE CAJA", subtitle_style))

    flujos_data = [['Período', 'Año', 'Flujo de Caja', 'Valor Presente']]

    for _, row in df_flujos.head(20).iterrows():
        flujos_data.append([
            str(int(row['Periodo'])),
            f"{row['Año']:.2f}",
            formato_moneda(row['Flujo']),
            formato_moneda(row['Valor Presente'])
        ])

    if len(df_flujos) > 20:
        flujos_data.append(['...', '...', '...', '...'])

    tabla_flujos = Table(flujos_data, colWidths=[1 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    tabla_flujos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    story.append(tabla_flujos)

    if len(df_flujos) > 20:
        nota = Paragraph(f"<i>Nota: Se muestran los primeros 20 períodos de {len(df_flujos)} totales.</i>",
                         normal_style)
        story.append(Spacer(1, 0.1 * inch))
        story.append(nota)

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
    """Función para calcular la valoración del bono"""
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

    for i in range(1, total_periodos_bono + 1):
        if i == total_periodos_bono:
            flujo = cupon + valor_nominal
        else:
            flujo = cupon

        vp = flujo / ((1 + tasa_descuento_periodica) ** i)
        valor_presente_total += vp

        flujos.append({
            'Periodo': i,
            'Año': round(i / num_periodos_bono, 2),
            'Flujo': flujo,
            'Valor Presente': vp
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


def show_mod_c_form():
    st.header("📊 Módulo C: Valoración de Bonos")
    st.markdown("Calcula el valor presente de un bono según sus características y pagos periódicos.")
    
    # SECCIÓN DE EJEMPLO EDUCATIVO
    with st.expander("📚 Ejemplo Práctico: Evaluación de Cartera de Bonos", expanded=False):
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
        
        # Configuración
        presupuesto_total = st.number_input('💰 Presupuesto Disponible (S/)', 
                                           min_value=100000.0, value=500000.0, step=50000.0,
                                           help="Monto total que tienes para invertir")
        
        # Bonos predefinidos según el examen
        bonos_ejemplo = [
            {'Emisor': '🏢 Empresa A (Retail)', 'Tasa Cupón': 8.0, 'Años': 10,
             'Valor Nominal': 1000, 'Frecuencia': 'Semestral', 'Rendimiento Requerido': 7.0},
            {'Emisor': '🏭 Empresa B (Industrial)', 'Tasa Cupón': 6.0, 'Años': 5,
             'Valor Nominal': 1000, 'Frecuencia': 'Trimestral', 'Rendimiento Requerido': 7.5},
            {'Emisor': '💼 Empresa C (Servicios)', 'Tasa Cupón': 9.0, 'Años': 8,
             'Valor Nominal': 1000, 'Frecuencia': 'Anual', 'Rendimiento Requerido': 8.5}
        ]
        
        # Mostrar tabla de características con tooltips
        st.markdown("#### 📋 Características de los Bonos Disponibles")
        st.caption("Analiza cada característica para entender cómo afecta el valor del bono:")
        
        df_caracteristicas = pd.DataFrame([
            {
                'Empresa': b['Emisor'],
                'Cupón TEA': f"{b['Tasa Cupón']}%",
                'Plazo': f"{b['Años']} años",
                'VN': formato_moneda(b['Valor Nominal']),
                'Frecuencia': b['Frecuencia'],
                'Rend. Req.': f"{b['Rendimiento Requerido']}%"
            }
            for b in bonos_ejemplo
        ])
        
        st.dataframe(
            df_caracteristicas, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Empresa": st.column_config.TextColumn("Emisor", help="Empresa que emite el bono"),
                "Cupón TEA": st.column_config.TextColumn("Cupón TEA", help="Tasa de interés anual que paga el bono"),
                "Plazo": st.column_config.TextColumn("Plazo", help="Tiempo hasta el vencimiento"),
                "VN": st.column_config.TextColumn("Valor Nominal", help="Monto que se paga al vencimiento"),
                "Frecuencia": st.column_config.TextColumn("Frecuencia Pago", help="Periodicidad de pago de cupones"),
                "Rend. Req.": st.column_config.TextColumn("Rendimiento Req.", help="Tasa de retorno exigida por el mercado")
            }
        )
        
        # Calcular valoraciones
        resultados_ejemplo = []
        for bono in bonos_ejemplo:
            resultado = calcular_valoracion_bono(
                valor_nominal=bono['Valor Nominal'],
                tasa_cupon=bono['Tasa Cupón'],
                frecuencia_bono=bono['Frecuencia'],
                plazo_bono=bono['Años'],
                tea_bono=bono['Rendimiento Requerido']
            )
            resultado['emisor'] = bono['Emisor']
            resultado['valor_nominal'] = bono['Valor Nominal']
            resultado['rendimiento'] = bono['Rendimiento Requerido']
            resultados_ejemplo.append(resultado)
        
        # Análisis comparativo
        st.divider()
        st.markdown("**📊 Análisis de Valoración:**")
        
        col_analisis1, col_analisis2 = st.columns([2, 1])
        
        with col_analisis1:
            df_valoracion = pd.DataFrame([
                {
                    'Empresa': r['emisor'],
                    'VP': formato_moneda(r['valor_presente_total']),
                    'VN': formato_moneda(r['valor_nominal']),
                    'Diferencia': formato_moneda(r['valor_presente_total'] - r['valor_nominal']),
                    'Tipo': 'Prima' if r['valor_presente_total'] > r['valor_nominal'] 
                           else 'Descuento' if r['valor_presente_total'] < r['valor_nominal'] 
                           else 'Par',
                    '% sobre VN': f"{((r['valor_presente_total'] / r['valor_nominal'] - 1) * 100):.2f}%"
                }
                for r in resultados_ejemplo
            ])
            st.dataframe(df_valoracion, use_container_width=True, hide_index=True)
        
        with col_analisis2:
            # Gráfico de comparación
            fig_comparacion = go.Figure(data=[
                go.Bar(
                    x=[r['emisor'].split(' ')[1] for r in resultados_ejemplo],
                    y=[r['valor_presente_total'] for r in resultados_ejemplo],
                    marker_color=['#10B981' if r['valor_presente_total'] > r['valor_nominal']
                                 else '#EF4444' for r in resultados_ejemplo],
                    text=[formato_moneda(r['valor_presente_total']) for r in resultados_ejemplo],
                    textposition='auto',
                    hovertemplate='%{x}<br>VP: %{y:,.2f}<extra></extra>'
                )
            ])
            fig_comparacion.update_layout(
                title='Valor Presente',
                yaxis_title='Valor (S/)',
                height=250,
                template='plotly_white',
                showlegend=False
            )
            st.plotly_chart(fig_comparacion, use_container_width=True)
        
        # Interpretación
        st.divider()
        st.markdown("**💡 Interpretación:**")
        
        for r in resultados_ejemplo:
            diferencia = r['valor_presente_total'] - r['valor_nominal']
            porcentaje = (diferencia / r['valor_nominal']) * 100
            
            if diferencia > 1:
                st.success(f"✅ **{r['emisor']}**: Cotiza con **prima** de {formato_moneda(diferencia)} "
                          f"({porcentaje:+.2f}%). El cupón es superior al rendimiento del mercado, "
                          f"lo que hace al bono más atractivo.")
            elif diferencia < -1:
                st.warning(f"⚠️ **{r['emisor']}**: Cotiza con **descuento** de {formato_moneda(abs(diferencia))} "
                          f"({porcentaje:.2f}%). El cupón es inferior al rendimiento del mercado.")
            else:
                st.info(f"ℹ️ **{r['emisor']}**: Cotiza **a la par**. El cupón coincide con el rendimiento del mercado.")
        
        # Recomendación
        st.divider()
        st.markdown("**🎯 Recomendación de Inversión:**")
        
        # Ordenar por VP descendente
        resultados_ordenados = sorted(resultados_ejemplo, 
                                     key=lambda x: x['valor_presente_total'], 
                                     reverse=True)
        
        col_ranking1, col_ranking2 = st.columns([2, 3])
        
        with col_ranking1:
            st.markdown("**Ranking por Valor:**")
            for i, r in enumerate(resultados_ordenados):
                porcentaje = ((r['valor_presente_total'] / r['valor_nominal'] - 1) * 100)
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                st.write(f"{medal} **{i+1}. Empresa {r['emisor'].split(' ')[2]}**: "
                        f"{formato_moneda(r['valor_presente_total'])} ({porcentaje:+.2f}%)")
        
        with col_ranking2:
            mejor_bono = resultados_ordenados[0]
            cantidad_bonos = int(presupuesto_total / mejor_bono['valor_presente_total'])
            inversion_total = cantidad_bonos * mejor_bono['valor_presente_total']
            cupon_total_anual = cantidad_bonos * mejor_bono['cupon'] * mejor_bono['num_periodos_bono']
            
            st.info(f"""
            **Mejor opción: {mejor_bono['emisor']}**
            
            Con tu presupuesto de {formato_moneda(presupuesto_total)}:
            - Puedes comprar: **{cantidad_bonos} bonos**
            - Inversión total: {formato_moneda(inversion_total)}
            - Ingreso anual por cupones: {formato_moneda(cupon_total_anual)}
            - Cupón por período: {formato_moneda(mejor_bono['cupon'])} ({mejor_bono['num_periodos_bono']}x al año)
            """)
    
    # SECCIÓN PRINCIPAL: VALORACIÓN INDIVIDUAL
    st.divider()
    st.subheader("⚙️ Valoración Individual de Bono")
    
    # Tooltip de ayuda
    st.markdown("""
    <style>
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 300px;
        background-color: #555;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -150px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    <p style="color: #666; font-size: 14px;">
    <span class="tooltip">ℹ️ ¿Qué información necesito?
    <span class="tooltiptext">
    <b>Valor Nominal:</b> Monto que se recibe al vencimiento<br>
    <b>Tasa Cupón:</b> Tasa de interés anual que paga el bono<br>
    <b>Frecuencia:</b> Cada cuánto se pagan los cupones<br>
    <b>Plazo:</b> Años hasta el vencimiento<br>
    <b>Tasa Descuento:</b> Tasa de rendimiento requerida
    </span>
    </span>
    </p>
    """, unsafe_allow_html=True)
    
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
                "Frecuencia de Pago",
                ['Mensual', 'Bimestral', 'Trimestral', 'Cuatrimestral', 'Semestral', 'Anual'],
                index=4,
                help="Cada cuánto tiempo recibirás los cupones"
            )

            plazo_bono = st.number_input(
                "Plazo (Años)",
                min_value=1, max_value=50, value=5, step=1,
                help="Años hasta el vencimiento del bono"
            )

        with col3:
            tea_bono = st.number_input(
                "Tasa de Retorno Esperada (% TEA)",
                min_value=0.0, max_value=50.0, value=7.0, step=0.1,
                help="Tasa de descuento para calcular el valor presente"
            )

    # SECCIÓN 2: CÁLCULO AUTOMÁTICO (Sin botón, cálculo en tiempo real)
    st.divider()
    
    # Realizar cálculos
    resultados = calcular_valoracion_bono(
        valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono, tea_bono
    )

    # SECCIÓN 3: MOSTRAR RESULTADOS
    total_periodos = mostrar_resultados_completos(
        valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono,
        tea_bono, resultados['df_flujos'], resultados['valor_presente_total'],
        resultados['cupon'], resultados['tasa_cupon_periodica'],
        resultados['tasa_descuento_periodica'], resultados['num_periodos_bono']
    )

    # SECCIÓN 4: ANÁLISIS DE SENSIBILIDAD
    st.divider()
    st.subheader("📈 Análisis de Sensibilidad")
    
    # Gráfico de sensibilidad
    fig_sens = grafico_sensibilidad(
        valor_nominal, resultados['cupon'], resultados['total_periodos_bono'],
        frecuencia_bono, tea_bono, convertir_tea_a_periodica
    )
    st.plotly_chart(fig_sens, use_container_width=True)

    # SECCIÓN 5: COMPARACIÓN DE ESCENARIOS
    with st.expander("🔄 Comparar con diferentes tasas", expanded=False):
        col_comp1, col_comp2 = st.columns(2)

        with col_comp1:
            tasa_escenario1 = st.number_input(
                "Escenario Optimista - Tasa (%)",
                min_value=0.0,
                max_value=50.0,
                value=tea_bono - 2.0 if tea_bono > 2.0 else 1.0,
                step=0.1,
                key="tasa_esc1"
            )

        with col_comp2:
            tasa_escenario2 = st.number_input(
                "Escenario Pesimista - Tasa (%)",
                min_value=0.0,
                max_value=50.0,
                value=tea_bono + 2.0,
                step=0.1,
                key="tasa_esc2"
            )

        # Mostrar comparación
        comparacion_escenarios(
            tasa_escenario1, tasa_escenario2, tea_bono,
            valor_nominal, resultados['cupon'], resultados['total_periodos_bono'],
            frecuencia_bono, convertir_tea_a_periodica
        )

    # SECCIÓN 6: EXPORTACIÓN
    st.divider()

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        # Descarga CSV
        csv = resultados['df_flujos'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Flujos (CSV)",
            data=csv,
            file_name=f"valoracion_bono_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_btn2:
        # Descarga PDF
        try:
            pdf_buffer = generar_pdf_bonos(
                valor_nominal, tasa_cupon, frecuencia_bono, plazo_bono,
                tea_bono, resultados['df_flujos'], resultados['valor_presente_total'],
                resultados['cupon'], resultados['tasa_cupon_periodica'],
                resultados['tasa_descuento_periodica']
            )

            st.download_button(
                label="📄 Descargar Reporte (PDF)",
                data=pdf_buffer,
                file_name=f"reporte_bono_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error al generar PDF: {str(e)}")