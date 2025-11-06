import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils.utils import formato_moneda


def mostrar_metricas_bono(valor_presente_total, valor_nominal, cupon):
    """Muestra las métricas principales del bono"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💎 Valor Presente", formato_moneda(valor_presente_total))

    with col2:
        st.metric("📄 Valor Nominal", formato_moneda(valor_nominal))

    with col3:
        st.metric("💰 Cupón Periódico", formato_moneda(cupon))

    with col4:
        diferencia = valor_presente_total - valor_nominal
        if diferencia > 0:
            tipo = "🔺 Prima"
            color = "normal"
        elif diferencia < 0:
            tipo = "🔻 Descuento"
            color = "inverse"
        else:
            tipo = "➖ A la Par"
            color = "off"
        st.metric("Tipo de Bono", tipo, delta=formato_moneda(diferencia))


def mostrar_interpretacion(valor_presente_total, valor_nominal, tea_bono, tasa_cupon):
    """Muestra la interpretación del resultado de valoración"""
    diferencia = abs(valor_presente_total - valor_nominal)
    
    if valor_presente_total > valor_nominal:
        st.success(f"✅ **Bono con Prima (Sobre Par)**")
        st.write(f"- El VP es {formato_moneda(diferencia)} mayor que el valor nominal")
        st.info(f"💡 **Razón:** La tasa cupón ({tasa_cupon:.2f}%) es mayor que la tasa de descuento ({tea_bono:.2f}%), por lo que el bono vale más que su valor nominal.")
    elif valor_presente_total < valor_nominal:
        st.warning(f"⚠️ **Bono con Descuento (Bajo Par)**")
        st.write(f"- El VP es {formato_moneda(diferencia)} menor que el valor nominal")
        st.info(f"💡 **Razón:** La tasa cupón ({tasa_cupon:.2f}%) es menor que la tasa de descuento ({tea_bono:.2f}%), por lo que el bono vale menos que su valor nominal.")
    else:
        st.info("ℹ️ **Bono a la Par**")
        st.write("- El valor presente es igual al valor nominal")
        st.info("💡 **Razón:** La tasa cupón y la tasa de descuento son iguales.")


def grafico_flujos(df_flujos):
    """Genera el gráfico de flujos de caja vs valor presente"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=df_flujos['Flujo'],
        name='Flujo de Caja',
        marker_color='#3B82F6',
        hovertemplate='Año: %{x:.2f}<br>Flujo: $%{y:,.2f}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=df_flujos['Valor Presente'],
        name='Valor Presente',
        marker_color='#10B981',
        hovertemplate='Año: %{x:.2f}<br>VP: $%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Valor (USD)",
        barmode='group',
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )

    return fig


def grafico_vp_acumulado(df_flujos, valor_nominal):
    """Genera el gráfico de valor presente acumulado"""
    df_flujos_copy = df_flujos.copy()
    df_flujos_copy['VP Acumulado'] = df_flujos_copy['Valor Presente'].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_flujos_copy['Año'],
        y=df_flujos_copy['VP Acumulado'],
        mode='lines+markers',
        name='VP Acumulado',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.2)',
        hovertemplate='Año: %{x:.2f}<br>VP Acumulado: $%{y:,.2f}<extra></extra>'
    ))

    fig.add_hline(
        y=valor_nominal,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Valor Nominal: {formato_moneda(valor_nominal)}",
        annotation_position="right"
    )

    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Valor Presente Acumulado (USD)",
        height=400,
        template='plotly_white',
        hovermode='x'
    )

    return fig


def tabla_flujos(df_flujos):
    """Muestra la tabla de flujos formateada"""
    df_mostrar = df_flujos.copy()
    df_mostrar['Flujo'] = df_mostrar['Flujo'].apply(formato_moneda)
    df_mostrar['Valor Presente'] = df_mostrar['Valor Presente'].apply(formato_moneda)

    st.dataframe(
        df_mostrar,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Periodo": st.column_config.NumberColumn("Período", format="%d"),
            "Año": st.column_config.NumberColumn("Año", format="%.2f"),
            "Flujo": "Flujo de Caja",
            "Valor Presente": "Valor Presente"
        }
    )


def comparacion_escenarios(tasa_escenario1, tasa_escenario2, tea_bono,
                           valor_nominal, cupon, total_periodos_bono,
                           frecuencia_bono, convertir_tea_a_periodica):
    """Muestra la comparación de escenarios con diferentes tasas de forma visual"""
    from utils.utils import convertir_tea_a_periodica

    # Calcular escenarios
    tasa_esc1_periodica = convertir_tea_a_periodica(tasa_escenario1, frecuencia_bono)
    tasa_esc2_periodica = convertir_tea_a_periodica(tasa_escenario2, frecuencia_bono)
    tasa_actual_periodica = convertir_tea_a_periodica(tea_bono, frecuencia_bono)

    vp_esc1 = sum([
        (cupon if i < total_periodos_bono else cupon + valor_nominal) /
        ((1 + tasa_esc1_periodica) ** i)
        for i in range(1, total_periodos_bono + 1)
    ])

    vp_esc2 = sum([
        (cupon if i < total_periodos_bono else cupon + valor_nominal) /
        ((1 + tasa_esc2_periodica) ** i)
        for i in range(1, total_periodos_bono + 1)
    ])

    vp_actual = sum([
        (cupon if i < total_periodos_bono else cupon + valor_nominal) /
        ((1 + tasa_actual_periodica) ** i)
        for i in range(1, total_periodos_bono + 1)
    ])

    # Mostrar comparación en columnas
    st.markdown("### Comparación de Valores Presentes")
    
    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        diff1 = vp_esc1 - valor_nominal
        st.metric(
            f"📉 Escenario Optimista",
            formato_moneda(vp_esc1),
            delta=formato_moneda(diff1),
            help=f"Tasa: {tasa_escenario1}%"
        )

    with col_res2:
        diff_actual = vp_actual - valor_nominal
        st.metric(
            f"🎯 Escenario Base",
            formato_moneda(vp_actual),
            delta=formato_moneda(diff_actual),
            help=f"Tasa: {tea_bono}%"
        )

    with col_res3:
        diff2 = vp_esc2 - valor_nominal
        st.metric(
            f"📈 Escenario Pesimista",
            formato_moneda(vp_esc2),
            delta=formato_moneda(diff2),
            help=f"Tasa: {tasa_escenario2}%"
        )

    return vp_esc1, vp_actual, vp_esc2


def grafico_sensibilidad(valor_nominal, cupon, total_periodos_bono,
                         frecuencia_bono, tea_bono, convertir_tea_a_periodica):
    """Genera el gráfico de análisis de sensibilidad"""
    from utils.utils import convertir_tea_a_periodica

    # Gráfica de sensibilidad
    tasas_rango = [i / 10 for i in range(10, 201, 5)]  # 1% a 20%
    valores_sensibilidad = []

    for tasa in tasas_rango:
        tasa_per = convertir_tea_a_periodica(tasa, frecuencia_bono)
        vp = sum([
            (cupon if i < total_periodos_bono else cupon + valor_nominal) /
            ((1 + tasa_per) ** i)
            for i in range(1, total_periodos_bono + 1)
        ])
        valores_sensibilidad.append(vp)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tasas_rango,
        y=valores_sensibilidad,
        mode='lines',
        name='Valor del Bono',
        line=dict(color='#6366f1', width=3),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.2)'
    ))

    fig.add_hline(
        y=valor_nominal,
        line_dash="dash",
        line_color="red",
        annotation_text="Valor Nominal"
    )

    fig.add_vline(
        x=tea_bono,
        line_dash="dot",
        line_color="green",
        annotation_text="Tasa Actual"
    )

    fig.update_layout(
        title="Análisis de Sensibilidad: Valor del Bono vs Tasa de Descuento",
        xaxis_title="Tasa de Descuento (%)",
        yaxis_title="Valor Presente (USD)",
        height=400,
        template='plotly_white'
    )

    return fig


def mostrar_resultados_completos(valor_nominal, tasa_cupon, frecuencia_bono,
                                 plazo_bono, tea_bono, df_flujos,
                                 valor_presente_total, cupon,
                                 tasa_cupon_periodica, tasa_descuento_periodica,
                                 num_periodos_bono):
    """Función principal que muestra todos los resultados de forma concisa"""
    total_periodos_bono = plazo_bono * num_periodos_bono

    # Métricas principales
    st.subheader("📊 Resultados de la Valoración")
    mostrar_metricas_bono(valor_presente_total, valor_nominal, cupon)

    # Interpretación
    st.divider()
    mostrar_interpretacion(valor_presente_total, valor_nominal, tea_bono, tasa_cupon)

    # Resumen en dos columnas
    st.divider()
    st.subheader("📌 Resumen de Parámetros")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Valor Nominal:** {formato_moneda(valor_nominal)}")
        st.write(f"**Tasa Cupón (TEA):** {tasa_cupon}%")
        st.write(f"**Tasa Cupón Periódica:** {tasa_cupon_periodica * 100:.4f}%")
        st.write(f"**Cupón por Período:** {formato_moneda(cupon)}")

    with col2:
        st.write(f"**Frecuencia:** {frecuencia_bono}")
        st.write(f"**Plazo:** {plazo_bono} años ({total_periodos_bono} períodos)")
        st.write(f"**Tasa de Descuento (TEA):** {tea_bono}%")
        st.write(f"**Tasa Descuento Periódica:** {tasa_descuento_periodica * 100:.4f}%")

    # Gráficos
    st.divider()
    st.subheader("🔎 Análisis Visual")
    
    tab1, tab2, tab3 = st.tabs(["💵 Flujos de Caja", "📊 VP Acumulado", "📋 Tabla Detallada"])
    
    with tab1:
        fig_flujos = grafico_flujos(df_flujos)
        st.plotly_chart(fig_flujos, use_container_width=True)
    
    with tab2:
        fig_acumulado = grafico_vp_acumulado(df_flujos, valor_nominal)
        st.plotly_chart(fig_acumulado, use_container_width=True)
    
    with tab3:
        tabla_flujos(df_flujos)

    return total_periodos_bono