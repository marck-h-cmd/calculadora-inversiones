from utils.utils import convertir_tea_a_periodica, formato_moneda
import pandas as pd 
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import io
from utils.email import enviar_email_con_pdf_gmail
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from utils.gemini import generar_analisis_inversiones

st.markdown("""
<style>
/* Contenedor principal de métricas */
.metric-container .stMetric {
    background-color: #d1fae5 !important;  /* Verde clarito */
    color: black !important;               /* Texto negro */
    border-radius: 10px;                   /* Bordes redondeados */
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* Botones verdes brillantes */
.stButton>button {
    background-color: #10B981 !important;  /* Verde brillante */
    color: white !important;               /* Texto blanco */
    font-weight: bold;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    border: none;
}

.stButton>button:hover {
    background-color: #059669 !important;  /* Verde más intenso al pasar el mouse */
}
</style>
""", unsafe_allow_html=True)

def show_inversiones(nombre):
    st.divider()
    st.markdown("<br><h2>📈 Inversiones</h2>"
                "Calcula y vea cómo crece su capital en dólares según sus aportes e inversiones para el futuro."
                , unsafe_allow_html=True)
    
    # Parámetros y datos de entrada
    st.markdown("<br><h3> Parámetros y datos de entrada</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        edad_actual = st.number_input(
            "Edad Actual",
            min_value=18, value=30, step=1,
            help="Tu edad actual en años"
        )
        
        monto_inicial = st.number_input(
            "Monto Inicial (USD)",
            min_value=0.0, value=10000.0, step=100.0,
            help="Capital inicial que invertirás"
        )
    
    with col2:
        tipo_impuesto = st.selectbox(
            "Tipo de Impuesto a la renta",
            ['Bolsa Local (5%)', 'Bolsa Extranjera (29.5%)'],
            help="Impuesto aplicable según el origen de las inversiones"
        )

        if tipo_impuesto == "Bolsa Local (5%)":
            valor_impuesto = 0.05
        else:
            valor_impuesto = 0.295

        aporte_periodico = st.number_input(
            "Aporte Periódico (USD)",
            min_value=0.0, value=500.0, step=50.0,
            help="Cantidad que aportarás regularmente - Opcional"
        )
    
    with col3:
        tea_cartera = st.number_input(
            "Tasa Efectiva Anual (%)",
            min_value=1.0, max_value=50.0, value=8.0, step=0.1,
            help="Rentabilidad anual esperada (ej: 8% para fondos diversificados)"
        )

        frecuencia = st.selectbox(
            "Frecuencia de Aportes",
            ['Mensual', 'Bimestral', 'Trimestral', 'Cuatrimestral', 'Semestral', 'Anual'],
            help="Con qué regularidad realizarás tus aportes"
        )

    col1, col2 = st.columns(2)
    with col1:
        plazo_o_jubilacion = st.radio("Tiempo de retiro", ('Plazo (años)', 'Edad de Jubilación'), horizontal=True)

    with col2:
        if plazo_o_jubilacion == 'Plazo (años)':
            plazo_anios = st.number_input(
                "",
                min_value=1, max_value=70, value=30, step=1,
                help="Número de años que mantendrás tu inversión"
            )
        else:
            edad_jubilacion = st.number_input(
                "",
                min_value=edad_actual+1, max_value=100, step=1,
                help="Edad de jubilación hasta la cual mantendrás tu inversión"
            )
            plazo_anios = edad_jubilacion - edad_actual


    st.markdown("<br><h3>Opciones de jubilación</h3>", unsafe_allow_html=True)

    tipo_retiro = st.radio("Tipo de Retiro", ('Cobro total', 'Pensión Mensual'), help="Proyección de retiro (Cobro total al momento de la jubilación)  -  Pensión Mensual (Pago de dividendos mensuales)", horizontal=True)

    if tipo_retiro == 'Pensión Mensual':
        if tipo_impuesto != "Bolsa Local (5%)":
            st.warning("⚠️Debes seleccionar el tipo de impuesto a la renta --> Bolsa Local (5%)")
        else:
            tea_retiro = st.number_input(
                "TEA Durante Retiro (%)",
                min_value=1.0, max_value=50.0, value=tea_cartera, step=0.1,
                help="Rentabilidad esperada durante el retiro"
            )
    else:
        tea_retiro = None
    
    # Validaciones
    if monto_inicial == 0 and aporte_periodico == 0:
        st.warning("⚠️ Debes ingresar un monto inicial o un aporte periódico.")
    else:
        # Cálculos
        periodos_por_anio = {'Mensual': 12, 'Bimestral': 6, 'Trimestral': 4, 'Cuatrimestral': 3, 'Semestral': 2, 'Anual': 1}
        num_periodos = periodos_por_anio[frecuencia]
        total_periodos = plazo_anios * num_periodos
        tasa_periodica = convertir_tea_a_periodica(tea_cartera, frecuencia)
        
        # Simulación período a período
        saldo = monto_inicial
        saldo_inicial = monto_inicial
        datos = []
        
        datos.append({
            'Periodo': 0,
            'Edad': edad_actual,
            'Saldo Inicial': monto_inicial,
            'Intereses': 0,
            'Aporte': 0,
            'Saldo Final': monto_inicial,
            'Aportes Acumulados': monto_inicial
        })

        for i in range(1, total_periodos + 1):
            # valor futuro del monto inicial
            vf_inicial = saldo * (1 + tasa_periodica)**(i)

            # valor futuro de los aportes periodicos
            vf_aportes = aporte_periodico * ((1 + tasa_periodica)**(i) - 1) / tasa_periodica

            # ingresos totales
            saldo_final = vf_inicial + vf_aportes

            # costos totales
            aporte_acumulado = saldo + (aporte_periodico * i)

            # Intereses = Saldo final - aportes acumulados
            intereses = saldo_final - aporte_acumulado

            datos.append({
                'Periodo': i,
                'Edad': edad_actual + i // num_periodos,
                'Saldo Inicial': round(saldo_inicial, 2),
                'Intereses': round(intereses, 2),
                'Aporte': round(aporte_periodico, 2),
                'Saldo Final': round(saldo_final, 2),
                'Aportes Acumulados': round(aporte_acumulado, 2)
            })
        
        df_cartera = pd.DataFrame(datos)

        costos_totales = saldo + (aporte_periodico * total_periodos)
        ganancia_total = saldo_final - costos_totales
        impuesto = ganancia_total*valor_impuesto

        csv = df_cartera.to_csv(index=False).encode('utf-8')

        buffer_pdf = generar_pdf_inversion(monto_inicial,aporte_periodico,edad_actual,plazo_anios,frecuencia,tea_cartera,tipo_impuesto, valor_impuesto,tipo_retiro,saldo_final,costos_totales,ganancia_total,impuesto,
            cobro_total = (ganancia_total - impuesto) if tipo_retiro == "Cobro total" else 0,
            pension_mensual = locals().get("pension_mensual", 0) if tipo_retiro == "Pensión Mensual" else 0,
            df_cartera=df_cartera,
        )


        # Métricas principales
        st.divider()
        st.markdown("<h3> Resultados</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        if tipo_retiro == "Cobro total":
            with col1:
                st.metric(
                    " Ingresos totales",
                    formato_moneda(saldo_final),
                    f"A los {edad_actual + plazo_anios} años"
                )
            
            with col2:
                st.metric(
                    " Costos totales",
                    formato_moneda(costos_totales),
                    "Capital invertido"
                )
            
            with col3:
                st.metric(
                    " Renta total",
                    formato_moneda(ganancia_total),
                    f"{((ganancia_total/costos_totales)*100):.2f}% ROI"
                )


            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    f" Impuestos",
                    formato_moneda(impuesto),
                    delta=f"-{valor_impuesto*100}%",
                    delta_color="normal"
                )

            with col2:
                resultado = ganancia_total - impuesto

                if resultado > 0:
                    delta_texto = "Excelente ganancia"
                else:
                    delta_texto = "Mala pérdida"

                st.metric(
                    " Cobro total a retirar",
                    formato_moneda(resultado),
                    delta=delta_texto,
                )

        else:
            if tipo_impuesto == "Bolsa Local (5%)":

                tasa_cobro_mensual = 0.5 * (tea_retiro/100)
                dividendo_bruto_anual = saldo_final * tasa_cobro_mensual
                dividendos_neto_anual = dividendo_bruto_anual - dividendo_bruto_anual*valor_impuesto
                pension_mensual = dividendos_neto_anual / 12
                dividendos_totales_mensuales = dividendos_neto_anual * plazo_anios

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "💰 Ingresos totales",
                        formato_moneda(saldo_final),
                        f"A los {edad_actual + plazo_anios} años"
                    )

                with col2:
                    st.metric(
                        "Dividendo bruto anual",
                        formato_moneda(dividendo_bruto_anual),
                        delta="Dividendo anual antes de impuestos"
                    )

                with col3:
                    st.metric(
                        "Dividendo neto anual",
                        formato_moneda(dividendos_neto_anual),
                        delta="Dividendo anual después de impuestos"
                    )


                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "💵 Dividendos netos anuales",
                        formato_moneda(dividendos_totales_mensuales),
                        delta=f"Total de dinero a cobrar"
                    )

                with col2:
                    if pension_mensual > 0:
                        delta_texto = "Excelente pensión mensual"
                    else:
                        delta_texto = "Pésima pensión mensual"

                    st.metric(
                        "🎁🤑 Pensión mensual a cobrar",
                        formato_moneda(pension_mensual),
                        delta=delta_texto,
                    )

        st.divider()
        st.markdown("<h3>🧠 Análisis Inteligente</h3>", unsafe_allow_html=True)
        
        # Botón para generar análisis
        if st.button("📊 Obtener Análisis de Gemini", key="analisis_inversiones"):
            with st.spinner("🤖 Gemini está analizando tu estrategia de inversión..."):
                # Preparar datos para el análisis
                datos_analisis = {
                    'edad_actual': edad_actual,
                    'monto_inicial': monto_inicial,
                    'tipo_impuesto': tipo_impuesto,
                    'aporte_periodico': aporte_periodico,
                    'frecuencia_aportes': frecuencia,
                    'tea': tea_cartera,
                    'tiempo_retiro': f"{plazo_anios} años" if plazo_o_jubilacion == 'Plazo (años)' else f"Jubilación a {edad_jubilacion} años",
                    'tipo_retiro': tipo_retiro,
                    'tea_retiro': tea_retiro if tipo_retiro == 'Pensión Mensual' else None,
                    'ingresos_totales': saldo_final,
                    'costos_totales': costos_totales,
                    'renta_total': ganancia_total,
                    'roi': (ganancia_total/costos_totales)*100,
                    'impuestos': impuesto,
                    'cobro_total': resultado if tipo_retiro == 'Cobro total' else None,
                    'pension_mensual': dividendos_totales_mensuales if tipo_retiro == 'Pensión Mensual' else None,  
                    'cobro_mensual_bruto': dividendo_bruto_anual if tipo_retiro == 'Pensión Mensual' else None,
                }
                
                analisis = generar_analisis_inversiones(datos_analisis)
                
                # Mostrar análisis en un acordeón
                with st.expander("📋 **Análisis Detallado de tu Estrategia de Inversión**", expanded=True):
                    st.markdown(analisis)
        
        # Tabla detallada
        st.divider()
        st.subheader("📋 Reporte detallado del crecimiento del fondo")
        
        # Mostrar solo datos anuales
        df_mostrar = df_cartera[df_cartera['Periodo'] % num_periodos == 0].copy()
        df_mostrar['Saldo Inicial'] = df_mostrar['Saldo Inicial'].apply(formato_moneda)
        df_mostrar['Intereses'] = df_mostrar['Intereses'].apply(formato_moneda)
        df_mostrar['Aportes Acumulados'] = df_mostrar['Aportes Acumulados'].apply(formato_moneda)
        df_mostrar['Saldo Final'] = df_mostrar['Saldo Final'].apply(formato_moneda)
        
        st.dataframe(
            df_mostrar[['Periodo', 'Edad', 'Saldo Inicial', 'Intereses', 'Aportes Acumulados', 'Saldo Final']],
            use_container_width=True,
            hide_index=True
        )


        # Gráfica de crecimiento
        st.divider()
        st.subheader("📊 Gráfica del crecimiento de la cartera")
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_cartera['Edad'],
            y=df_cartera['Aportes Acumulados'],
            mode='lines',
            name='Aportes Acumulados',
            fill='tozeroy',
            line=dict(color='#3B82F6', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_cartera['Edad'],
            y=df_cartera['Saldo Final'],
            mode='lines',
            name='Capital Total (Ingresos totales)',
            fill='tonexty',
            line=dict(color='#10B981', width=2)
        ))
        
        fig.update_layout(
            xaxis_title="Edad (años)",
            yaxis_title="Valor (USD)",
            hovermode='x unified',
            height=450,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)


        st.divider()

        st.subheader("🔄 Comparación de Escenarios")
        comparar = st.radio(
            "Deseo comparar",
            [
                "Comparar con otra edad de jubilación",
                "Comparar con otra Tasa Efectiva Anual (%)"
            ], horizontal=True
        )

        #COMPARACION
        if comparar == "Comparar con otra edad de jubilación":
            col1, col2 = st.columns(2)
            with col1:
                edad_comp_1 = st.number_input(
                    "Edad de jubilación - Opción A",
                    min_value=edad_actual+1, max_value=100, step=1
                )
            
            with col2:
                edad_comp_2 = st.number_input(
                    "Edad de jubilación - Opción B",
                    min_value=edad_actual+1, max_value=100, step=1
                )

        else:
            col1, col2 = st.columns(2)
            with col1:
                tasa_1 = st.number_input(
                    "TEA % - Opción A",
                    min_value=1.0, max_value=50.0, value=8.0, step=0.1
                )
            
            with col2:
                tasa_2 = st.number_input(
                    "TEA % - Opción B",
                    min_value=1.0, max_value=50.0, value=8.0, step=0.1
                )



        def simulacion_calcular_cobroTotal(monto_inicial, num_periodos, edad_jubilacion, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia):
            plazo_anios = edad_jubilacion - edad_actual
            total_periodos = plazo_anios * num_periodos
            tasa_periodica = convertir_tea_a_periodica(tea_cartera, frecuencia)
            saldo = monto_inicial
            saldo_final = monto_inicial

            datos = []
        
            datos.append({
                'Periodo': 0,
                'Edad': edad_actual,
                'Saldo Inicial': monto_inicial,
                'Intereses': 0,
                'Aporte': 0,
                'Saldo Final': monto_inicial,
                'Aportes Acumulados': monto_inicial
            })


            for i in range(1, total_periodos + 1):

                vf_inicial = saldo * (1 + tasa_periodica) ** i

                vf_aportes = aporte_periodico * ((1 + tasa_periodica) ** i - 1) / tasa_periodica

                # ingresos totales
                saldo_final = vf_inicial + vf_aportes

            # Cálculos finales de impuestos y métricas
            costos_totales = saldo + (aporte_periodico * total_periodos)
            ganancia_total = saldo_final - costos_totales
            impuesto = ganancia_total * valor_impuesto
            cobro_total = ganancia_total - impuesto

            return cobro_total
        


        def simulacion_calcular_pensionMensual(monto_inicial, num_periodos, edad_jubilacion, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia, tea_retiro):
            plazo_anios = edad_jubilacion - edad_actual
            total_periodos = plazo_anios * num_periodos
            tasa_periodica = convertir_tea_a_periodica(tea_cartera, frecuencia)
            saldo = monto_inicial
            saldo_final = monto_inicial

            datos = []
        
            datos.append({
                'Periodo': 0,
                'Edad': edad_actual,
                'Saldo Inicial': monto_inicial,
                'Intereses': 0,
                'Aporte': 0,
                'Saldo Final': monto_inicial,
                'Aportes Acumulados': monto_inicial
            })


            for i in range(1, total_periodos + 1):

                vf_inicial = saldo * (1 + tasa_periodica) ** i

                vf_aportes = aporte_periodico * ((1 + tasa_periodica) ** i - 1) / tasa_periodica

                # ingresos totales
                saldo_final = vf_inicial + vf_aportes


            tasa_cobro_mensual = 0.5 * (tea_retiro/100)
            dividendo_bruto_anual = saldo_final * tasa_cobro_mensual
            dividendos_neto_anual = dividendo_bruto_anual - dividendo_bruto_anual*valor_impuesto
            pension_mensual = dividendos_neto_anual / 12

            return pension_mensual



        # Mostrar resultados lado a lado
        st.divider()
        st.markdown("### 📈 Resultados comparativos")

        if comparar == "Comparar con otra edad de jubilación":
            if tipo_retiro == "Cobro total":
                cobro_total_1 = simulacion_calcular_cobroTotal(monto_inicial, num_periodos, edad_comp_1, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia)

                cobro_total_2 = simulacion_calcular_cobroTotal(monto_inicial, num_periodos, edad_comp_2, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Opción A**")
                    st.metric(" Cobro total a retirar", formato_moneda(cobro_total_1))

                with c2:
                    st.markdown(f"**Opción B**")
                    st.metric(" Cobro total a retirar", formato_moneda(cobro_total_2))
                    
                # Comparación simple: cuál conviene más
                mejor = "A" if cobro_total_1 > cobro_total_2 else "B"
                diferencia = abs(cobro_total_1 - cobro_total_2)
                st.markdown(f"**Conclusión:** La mejor opción es **{mejor}** — Diferencia neta: {formato_moneda(diferencia)}")

            else:
                pension_mensual_1 = simulacion_calcular_pensionMensual(monto_inicial, num_periodos, edad_comp_1, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia, tea_retiro)

                pension_mensual_2 = simulacion_calcular_pensionMensual(monto_inicial, num_periodos, edad_comp_2, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia, tea_retiro)


                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Opción A**")
                    st.metric("🎁🤑 Pensión mensual a cobrar", formato_moneda(pension_mensual_1))

                with c2:
                    st.markdown(f"**Opción B**")
                    st.metric("🎁🤑 Pensión mensual a cobrar", formato_moneda(pension_mensual_2))

                # Comparación simple: cuál conviene más
                mejor = "A" if pension_mensual_1 > pension_mensual_2 else "B"
                diferencia = abs(pension_mensual_1 - pension_mensual_2)
                st.markdown(f"**Conclusión:** La mejor opción es **{mejor}** — Diferencia neta: {formato_moneda(diferencia)}")


        else:
            if tipo_retiro == "Cobro total":
                cobro_total_3 = simulacion_calcular_cobroTotal(monto_inicial, num_periodos, edad_actual + plazo_anios, edad_actual, valor_impuesto, aporte_periodico, tasa_1, frecuencia)

                cobro_total_4 = simulacion_calcular_cobroTotal(monto_inicial, num_periodos, edad_actual + plazo_anios, edad_actual, valor_impuesto, aporte_periodico, tasa_2, frecuencia)


                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Opción A**")
                    st.metric("🎁🤑 Cobro total a retirar", formato_moneda(cobro_total_3))

                with c2:
                    st.markdown(f"**Opción B**")
                    st.metric("🎁🤑 Cobro total a retirar", formato_moneda(cobro_total_4))

                # Comparación simple: cuál conviene más
                mejor = "A" if cobro_total_3 > cobro_total_4 else "B"
                diferencia = abs(cobro_total_3 - cobro_total_4)
                st.markdown(f"**Conclusión:** La mejor opción es **{mejor}** — Diferencia neta: {formato_moneda(diferencia)}")

            else:
                pension_mensual_3 = simulacion_calcular_pensionMensual(monto_inicial, num_periodos, edad_actual + plazo_anios, edad_actual, valor_impuesto, aporte_periodico, tasa_1, frecuencia, tea_retiro)

                pension_mensual_4 = simulacion_calcular_pensionMensual(monto_inicial, num_periodos, edad_actual + plazo_anios, edad_actual, valor_impuesto, aporte_periodico, tasa_2, frecuencia, tea_retiro)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Opción A**")
                    st.metric("🎁🤑 Pensión mensual a cobrar", formato_moneda(pension_mensual_3))

                with c2:
                    st.markdown(f"**Opción B**")
                    st.metric("🎁🤑 Pensión mensual a cobrar", formato_moneda(pension_mensual_4))

                # Comparación simple: cuál conviene más
                mejor = "A" if pension_mensual_3 > pension_mensual_4 else "B"
                diferencia = abs(pension_mensual_3 - pension_mensual_3)
                st.markdown(f"**Conclusión:** La mejor opción es **{mejor}** — Diferencia neta: {formato_moneda(diferencia)}")
            
        st.divider()

        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                label="📄 Descargar reporte PDF",
                data=buffer_pdf.getvalue(),
                file_name=f"reporte_inversion_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

        with d2:
            st.download_button(
                label="📥 Descargar datos en CSV",
                data=csv,
                file_name=f"proyeccion_cartera_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        with d3:
            if st.button("📧 Enviar por Email", use_container_width=True, key="email_bonos"):
                email_dest = st.session_state.get('email_destinatario')
                nombre_dest = st.session_state.get('nombre_usuario', 'Usuario')
                if nombre_dest == "":
                    nombre_dest = "Usuario"

                if email_dest:
                    metricas = {}

                    # Crear copia del buffer
                    pdf_buffer_email = io.BytesIO(buffer_pdf.getvalue())

                    with st.spinner("📤 Enviando reporte..."):
                        exito, resultado = enviar_email_con_pdf_gmail(
                            email_dest,
                            nombre_dest,
                            pdf_buffer_email,
                            "Inversiones",
                            metricas
                        )

                        if exito:
                            st.success(f"✅ Reporte enviado exitosamente a **{email_dest}**")
                        else:
                            st.error(f"❌ Error al enviar: {resultado}")
                else:
                    st.warning("⚠️ Por favor ingresa tu correo en el panel lateral")



def generar_pdf_inversion(
    monto_inicial: float,
    aporte_periodico: float,
    edad_actual: int,
    plazo_anios: int,
    frecuencia: str,
    tea_cartera: float,
    tipo_impuesto: str,
    valor_impuesto: float,
    tipo_retiro: str,
    saldo_final: float,
    costos_totales: float,
    ganancia_total: float,
    impuesto: float,
    cobro_total: float = None,
    pension_mensual: float = None,
    df_cartera=None,
    autor: str = "Calculadora de Inversiones Financieras"
) -> io.BytesIO:

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch
    )
    story = []
    styles = getSampleStyleSheet()

    # ---- Estilos ----
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER,
        textColor=colors.HexColor('#0b4c86'), spaceAfter=12, fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Heading2'], fontSize=13, alignment=TA_LEFT,
        textColor=colors.HexColor('#1f78b4'), spaceAfter=8, fontName='Helvetica-Bold'
    )
    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'], fontSize=10, leading=12, spaceAfter=6
    )

    # ---- Header ----
    story.append(Paragraph("REPORTE DE INVERSIÓN - PROYECCIÓN DE CARTERA", title_style))
    story.append(Spacer(1, 0.15 * inch))

    # ---- 1. Parámetros de entrada ----
    story.append(Paragraph("1. Parámetros de entrada", subtitle_style))

    parametros = [
        ["Parámetro", "Valor"],
        ["Edad actual", str(edad_actual)],
        ["Plazo (años)", str(plazo_anios)],
        ["Frecuencia de aportes", frecuencia],
        ["Monto inicial (USD)", formato_moneda(monto_inicial)],
        ["Aporte periódico (USD)", formato_moneda(aporte_periodico)],
        ["Tasa efectiva anual esperada (TEA)", f"{tea_cartera:.2f}%"],
        ["Tipo de impuesto", tipo_impuesto],
        ["Porcentaje de impuesto aplicado", f"{valor_impuesto*100:.2f}%"]
    ]

    # Solo incluir tipo de retiro si está definido
    if tipo_retiro:
        parametros.append(["Tipo de retiro proyectado", tipo_retiro])

    tabla_param = Table(parametros, colWidths=[3.2 * inch, 2.8 * inch])
    tabla_param.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f78b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))
    story.append(tabla_param)
    story.append(Spacer(1, 0.18 * inch))

    # ---- 2. Resumen Ejecutivo ----
    story.append(Paragraph("2. Resumen ejecutivo", subtitle_style))

    diferencia = saldo_final - monto_inicial
    resumen = [
        ["Métrica", "Valor"],
        ["Valor final proyectado (Ingresos totales)", formato_moneda(saldo_final)],
        ["Costos totales (capital invertido)", formato_moneda(costos_totales)],
        ["Ganancia / Renta total", formato_moneda(ganancia_total)],
        ["Impuesto estimado sobre ganancia", formato_moneda(impuesto)],
        ["Diferencia (valor final - monto inicial)", formato_moneda(diferencia)]
    ]

    # Agregar métrica según tipo de retiro
    if tipo_retiro == "Cobro total":
        if cobro_total is not None:
            resumen.append(["Cobro total proyectado (neto)", formato_moneda(cobro_total)])
    elif tipo_retiro == "Pensión mensual":
        if pension_mensual is not None:
            resumen.append(["Pensión mensual proyectada (neto)", formato_moneda(pension_mensual)])

    tabla_resumen = Table(resumen, colWidths=[3.2 * inch, 2.8 * inch])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    story.append(tabla_resumen)
    story.append(Spacer(1, 0.18 * inch))

    # ---- Interpretación ----
    if tipo_retiro == "Cobro total":
        if ganancia_total - impuesto > 0:
            interpretacion = "La proyección muestra una ganancia neta al momento del retiro. Revise el horizonte y la TEA para ajustar riesgo/retorno."
        else:
            interpretacion = "La proyección muestra una pérdida neta en este escenario. Considere aumentar la TEA proyectada o reducir costes."

    elif tipo_retiro == "Pensión mensual":
        if pension_mensual and pension_mensual > 0:
            interpretacion = f"La pensión mensual proyectada es {formato_moneda(pension_mensual)}. Valide si esto cubre su objetivo de ingreso."
        else:
            interpretacion = "La pensión proyectada es baja o nula bajo los supuestos actuales."

    else:
        interpretacion = "Escenario de retiro no definido."

    story.append(Paragraph(f"<b>Interpretación:</b> {interpretacion}", normal_style))
    story.append(Spacer(1, 0.20 * inch))

    # ---- 3. Reporte detallado anual ----
    story.append(Paragraph("3. Reporte detallado (resumen anual)", subtitle_style))

    try:
        periodos_por_anio = {'Mensual': 12, 'Bimestral': 6, 'Trimestral': 4, 'Cuatrimestral': 3, 'Semestral': 2, 'Anual': 1}
        num_periodos = periodos_por_anio.get(frecuencia, 12)

        if df_cartera is not None:
            df_mostrar = df_cartera[df_cartera['Periodo'] % num_periodos == 0].copy()

            tabla_head = ['Período', 'Edad', 'Saldo Inicial', 'Intereses', 'Aportes acumulados', 'Saldo final']
            fl = [tabla_head]

            for _, row in df_mostrar.iterrows():
                fl.append([
                    str(int(row.get('Periodo', ''))),
                    str(int(row.get('Edad', ''))),
                    formato_moneda(row.get('Saldo Inicial', 0)),
                    formato_moneda(row.get('Intereses', 0)),
                    formato_moneda(row.get('Aportes Acumulados', 0)),
                    formato_moneda(row.get('Saldo Final', 0)),
                ])

            if len(fl) > 25:
                fl = fl[:24] + [['...', '...', '...', '...', '...', '...']]
        else:
            fl = [
                ['Período', 'Edad', 'Saldo Inicial', 'Intereses', 'Aportes acumulados', 'Saldo final'],
                ['N/A', 'N/A', formato_moneda(0), formato_moneda(0), formato_moneda(0), formato_moneda(0)]
            ]
    except Exception as e:
        fl = [['Período', 'Edad', 'Saldo Inicial', 'Intereses', 'Aportes acumulados', 'Saldo final'],
              ['Error procesando tabla', str(e), '', '', '', '']]

    tabla_datos = Table(fl, colWidths=[0.8*inch, 0.8*inch, 1.2*inch, 1.0*inch, 1.3*inch, 1.3*inch])
    tabla_datos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    story.append(tabla_datos)
    story.append(Spacer(1, 0.16 * inch))

    if df_cartera is not None and len(df_cartera) // num_periodos > 24:
        story.append(Paragraph(f"<i>Nota:</i> Se muestran los primeros 24 períodos anuales de {len(df_cartera)//num_periodos} disponibles.", normal_style))
        story.append(Spacer(1, 0.12 * inch))

    # ---- Footer ----
    story.append(Spacer(1, 0.2 * inch))
    footer_text = (
        "Este reporte ha sido generado automáticamente por el sistema. Los resultados son estimaciones y no constituyen asesoría financiera."
    )
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(f"© {datetime.now().year} {autor}", ParagraphStyle('Copy', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))

    doc.build(story)
    buffer.seek(0)
    return buffer

