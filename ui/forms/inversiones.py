from utils.utils import convertir_tea_a_periodica, formato_moneda, mostrar_ayuda
import pandas as pd 
import streamlit as st
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils.gemini import generar_analisis_inversiones

def show_inversiones(nombre):
    st.divider()
    st.markdown("<br><h2>📈 Inversiones</h2>"
                "Calcula y vea cómo crece su capital en dólares según sus aportes e inversiones para el futuro."
                , unsafe_allow_html=True)
    
    # Parámetros y datos de entrada
    st.markdown("<br><h3>✏️ Parámetros y datos de entrada</h3>", unsafe_allow_html=True)

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


    st.markdown("<br><h3>🎯 Opciones de jubilación</h3>", unsafe_allow_html=True)

    tipo_retiro = st.radio("Tipo de Retiro", ('Cobro total', 'Pensión Mensual'), help="Proyección de retiro (Cobro total al momento de la jubilación)  -  Pensión Mensual (Pago de dividendos mensuales)", horizontal=True)

    if tipo_retiro == 'Pensión Mensual':
        if tipo_impuesto != "Bolsa Local (5%)":
            st.warning("⚠️ Debes seleccionar el tipo de impuesto a la renta --> Bolsa Local (5%)")
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

        
        # Métricas principales
        st.divider()
        st.markdown("<h3>🚀 Resultados</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        if tipo_retiro == "Cobro total":
            with col1:
                st.metric(
                    "💰 Ingresos totales",
                    formato_moneda(saldo_final),
                    f"A los {edad_actual + plazo_anios} años"
                )
            
            with col2:
                st.metric(
                    "💵 Costos totales",
                    formato_moneda(costos_totales),
                    "Capital invertido"
                )
            
            with col3:
                st.metric(
                    "📈 Renta total",
                    formato_moneda(ganancia_total),
                    f"{((ganancia_total/costos_totales)*100):.2f}% ROI"
                )


            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    f"😭 Impuestos",
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
                    "🎁🤑 Cobro total a retirar",
                    formato_moneda(resultado),
                    delta=delta_texto,
                )

        else:
            if tipo_impuesto == "Bolsa Local (5%)":

                tea_retiro = convertir_tea_a_periodica(tea_retiro, "Mensual")
                tasa_cobro_mensual = 0.5 * tea_retiro
                cobroMensual = saldo_final * tasa_cobro_mensual
                dividendos_antes_impuestos = saldo_final - cobroMensual
                impuesto_mensual = 0.05 * dividendos_antes_impuestos
                dividendos_finales = dividendos_antes_impuestos - impuesto_mensual

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "💰 Ingresos totales",
                        formato_moneda(saldo_final),
                        f"A los {edad_actual + plazo_anios} años"
                    )

                with col2:
                    st.metric(
                        "🗓️ Cobro mensual",
                        formato_moneda(cobroMensual),
                        delta=f"-{(tasa_cobro_mensual*100):.2f}% de los ingresos totales",
                        delta_color="normal"
                    )

                with col3:
                    st.metric(
                        "😲 Dividendos antes de impuestos",
                        formato_moneda(dividendos_antes_impuestos),
                        delta="Ingresos - Costo mensual"
                    )


                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        f"😭 Impuestos",
                        formato_moneda(impuesto_mensual),
                        delta=f"-{valor_impuesto*100}%",
                        delta_color="normal"
                    )

                with col2:
                    if dividendos_finales > 0:
                        delta_texto = "Excelente pensión mensual"
                    else:
                        delta_texto = "Pésima pensión mensual"

                    st.metric(
                        "🎁🤑 Pensión mensual a cobrar",
                        formato_moneda(dividendos_finales),
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
                'pension_mensual': dividendos_finales if tipo_retiro == 'Pensión Mensual' else None,  
                'cobro_mensual_bruto': cobroMensual if tipo_retiro == 'Pensión Mensual' else None,
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


        
        # Botón de descarga
        csv = df_cartera.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar datos en CSV",
            data=csv,
            file_name=f"proyeccion_cartera_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


        st.divider()

        st.subheader("🔄 Comparación de Escenarios")
        comparar = st.radio(
            "📊 Deseo comparar",
            [
                "Comparar con otra edad de jubilación",
                "Comparar con otra tasa de retorno (TEA)"
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
                    "TEA de retorno - Opción A",
                    min_value=1.0, max_value=50.0, value=8.0, step=0.1
                )
            
            with col2:
                tasa_2 = st.number_input(
                    "TEA de retorno - Opción B",
                    min_value=1.0, max_value=50.0, value=8.0, step=0.1
                )



        def simulacion_comparar_jubilacion(monto_inicial, num_periodos, edad_jubilacion, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia):
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

            # Cálculos finales de impuestos y métricas
            costos_totales = saldo + (aporte_periodico * total_periodos)
            ganancia_total = saldo_final - costos_totales
            impuesto = ganancia_total * valor_impuesto
            cobro_total = ganancia_total - impuesto

            tea_retiro = convertir_tea_a_periodica(tea_cartera, "Mensual")

            tasa_cobro_mensual = 0.5 * tea_retiro
            cobroMensual = saldo_final * tasa_cobro_mensual
            dividendos_antes_impuestos = saldo_final - cobroMensual
            impuesto_mensual = 0.05 * dividendos_antes_impuestos
            dividendos_finales = dividendos_antes_impuestos - impuesto_mensual

            return {
                "edad_jubilacion": edad_jubilacion,
                "plazo_anios": plazo_anios,
                "saldo_final": saldo_final,
                "resultado_cobro_total_neto": cobro_total,
                "ganancia_total": ganancia_total,
                "dividendos_finales": dividendos_finales,
                "cobroMensual": cobroMensual,
                "dividendos_antes_impuestos": dividendos_antes_impuestos,
                "impuesto_mensual": impuesto_mensual,
                "dividendos_finales": dividendos_finales,
                "df_cartera": df_cartera
            }

        def simulacion_comparar_tasas(monto_inicial, num_periodos, plazo, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia):
            plazo_anios = plazo
            edad_jubilacion = edad_actual + plazo
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

            # Cálculos finales de impuestos y métricas
            costos_totales = saldo + (aporte_periodico * total_periodos)
            ganancia_total = saldo_final - costos_totales
            impuesto = ganancia_total * valor_impuesto
            cobro_total = ganancia_total - impuesto

            tea_retiro = convertir_tea_a_periodica(tea_cartera, "Mensual")

            tasa_cobro_mensual = 0.5 * tea_retiro
            cobroMensual = saldo_final * tasa_cobro_mensual
            dividendos_antes_impuestos = saldo_final - cobroMensual
            impuesto_mensual = 0.05 * dividendos_antes_impuestos
            dividendos_finales = dividendos_antes_impuestos - impuesto_mensual

            return {
                "edad_jubilacion": edad_jubilacion,
                "plazo_anios": plazo_anios,
                "saldo_final": saldo_final,
                "resultado_cobro_total_neto": cobro_total,
                "ganancia_total": ganancia_total,
                "dividendos_finales": dividendos_finales,
                "cobroMensual": cobroMensual,
                "dividendos_antes_impuestos": dividendos_antes_impuestos,
                "impuesto_mensual": impuesto_mensual,
                "dividendos_finales": dividendos_finales,
                "df_cartera": df_cartera
            }


        # Ejecutar escenarios
        if comparar == "Comparar con otra edad de jubilación":
            esc1 = simulacion_comparar_jubilacion(monto_inicial, num_periodos, edad_comp_1, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia)
            esc2 = simulacion_comparar_jubilacion(monto_inicial, num_periodos, edad_comp_2, edad_actual, valor_impuesto, aporte_periodico, tea_cartera, frecuencia)
        else:
            esc1 = simulacion_comparar_tasas(monto_inicial, num_periodos, plazo_anios, edad_actual, valor_impuesto, aporte_periodico, tasa_1, frecuencia)
            esc2 = simulacion_comparar_tasas(monto_inicial, num_periodos, plazo_anios, edad_actual, valor_impuesto, aporte_periodico, tasa_2, frecuencia)


        # Mostrar resultados lado a lado
        st.divider()
        st.markdown("### 📈 Resultados comparativos")

        if tipo_retiro == "Cobro total":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Opción A**")
                st.metric("🎁🤑 Cobro total a retirar", formato_moneda(esc1['resultado_cobro_total_neto']), delta="")

            with c2:
                
                st.markdown(f"**Opción B**")
                st.metric("🎁🤑 Cobro total a retirar", formato_moneda(esc2['resultado_cobro_total_neto']), delta="")

            # Comparación simple: cuál conviene más
            mejor = "A" if esc1['resultado_cobro_total_neto'] > esc2['resultado_cobro_total_neto'] else "B"
            diferencia = abs(esc1['resultado_cobro_total_neto'] - esc2['resultado_cobro_total_neto'])
            st.markdown(f"**Conclusión:** La mejor opción es **{mejor}** — Diferencia neta: {formato_moneda(diferencia)}")
            st.subheader("📊 Comparativa del crecimiento de la cartera según edad de jubilación")



        else:  #"Pensión Mensual"
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Opción A**")
                st.metric("🎁🤑 Pensión mensual a cobrar", formato_moneda(esc1['dividendos_finales']), delta="")

            with c2:
                st.markdown(f"**Opción B**")
                st.metric("🎁🤑 Pensión mensual a cobrar", formato_moneda(esc2['dividendos_finales']), delta="")

            mejor = "A" if esc1['dividendos_finales'] > esc2['dividendos_finales'] else "B"
            diferencia = abs(esc1['dividendos_finales'] - esc2['dividendos_finales'])
            st.markdown(f"**Conclusión:** La mejor opción es **{mejor}** — Diferencia mensual: {formato_moneda(diferencia)}")
            st.subheader("📊 Comparativa del crecimiento de la cartera según pensión mensual")


        if comparar == "Comparar con otra edad de jubilación":
            fig = go.Figure()

            # Escenario A
            fig.add_trace(go.Scatter(
                x=esc1['df_cartera']['Edad'],
                y=esc1['df_cartera']['Aportes Acumulados'],
                mode='lines',
                name=f'Aportes Acumulados (Jubilarse a {esc1["edad_jubilacion"]})',
                fill='tozeroy',
                line=dict(color="#1E88E5", width=2)   # Azul
            ))

            fig.add_trace(go.Scatter(
                x=esc1['df_cartera']['Edad'],
                y=esc1['df_cartera']['Saldo Final'],
                mode='lines',
                name=f'Capital Total (Jubilarse a {esc1["edad_jubilacion"]})',
                fill='tozeroy',
                line=dict(color="#43A047", width=2)   # Verde
            ))


            # Escenario B
            fig.add_trace(go.Scatter(
                x=esc2['df_cartera']['Edad'],
                y=esc2['df_cartera']['Aportes Acumulados'],
                mode='lines',
                name=f'Aportes Acumulados (Jubilarse a {esc2["edad_jubilacion"]})',
                fill='tozeroy',
                line=dict(color="#FB8C00", width=2)   # Naranja
            ))

            fig.add_trace(go.Scatter(
                x=esc2['df_cartera']['Edad'],
                y=esc2['df_cartera']['Saldo Final'],
                mode='lines',
                name=f'Capital Total (Jubilarse a {esc2["edad_jubilacion"]})',
                fill='tozeroy',
                line=dict(color="#8E24AA", width=2)   # Morado
            ))

            fig.update_layout(
                xaxis_title="Edad (años)",
                yaxis_title="Valor (USD)",
                hovermode='x unified',
                height=450,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)


        else:
            fig = go.Figure()

            # Escenario A
            fig.add_trace(go.Scatter(
                x=esc1['df_cartera']['Edad'],
                y=esc1['df_cartera']['Aportes Acumulados'],
                mode='lines',
                name=f'Aportes Acumulados (TEA {tasa_1}%)',
                fill='tozeroy',
                line=dict(color="#1E88E5", width=2)   # Azul
            ))

            fig.add_trace(go.Scatter(
                x=esc1['df_cartera']['Edad'],
                y=esc1['df_cartera']['Saldo Final'],
                mode='lines',
                name=f'Capital Total (TEA {tasa_1}%)',
                fill='tozeroy',
                line=dict(color="#43A047", width=2)   # Verde
            ))


            # Escenario B
            fig.add_trace(go.Scatter(
                x=esc2['df_cartera']['Edad'],
                y=esc2['df_cartera']['Aportes Acumulados'],
                mode='lines',
                name=f'Aportes Acumulados (TEA {tasa_2}%)',
                fill='tozeroy',
                line=dict(color="#FB8C00", width=2)   # Naranja
            ))

            fig.add_trace(go.Scatter(
                x=esc2['df_cartera']['Edad'],
                y=esc2['df_cartera']['Saldo Final'],
                mode='lines',
                name=f'Capital Total (TEA {tasa_2}%)',
                fill='tozeroy',
                line=dict(color="#8E24AA", width=2)   # Morado
            ))

            fig.update_layout(
                xaxis_title="Edad (años)",
                yaxis_title="Valor (USD)",
                hovermode='x unified',
                height=450,
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)