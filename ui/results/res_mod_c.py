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
        tipo = "Premium" if diferencia > 0 else "Descuento" if diferencia < 0 else "Par"
        st.metric("Tipo de Bono", tipo, delta=formato_moneda(diferencia))


def mostrar_interpretacion(valor_presente_total, valor_nominal, tea_bono, tasa_cupon):
    """Muestra la interpretación del resultado de valoración"""
    if valor_presente_total > valor_nominal:
        st.success(
            f"✅ El bono cotiza con **prima** (sobre par). El VP es {formato_moneda(valor_presente_total - valor_nominal)} mayor que el valor nominal.")
        st.info(
            "💡 **Interpretación:** Como la tasa de descuento ({:.2f}%) es menor que la tasa cupón ({:.2f}%), el bono vale más que su valor nominal.".format(
                tea_bono, tasa_cupon))
    elif valor_presente_total < valor_nominal:
        st.warning(
            f"⚠️ El bono cotiza con **descuento** (bajo par). El VP es {formato_moneda(valor_nominal - valor_presente_total)} menor que el valor nominal.")
        st.info(
            "💡 **Interpretación:** Como la tasa de descuento ({:.2f}%) es mayor que la tasa cupón ({:.2f}%), el bono vale menos que su valor nominal.".format(
                tea_bono, tasa_cupon))
    else:
        st.info("ℹ️ El bono cotiza **a la par**. El valor presente es igual al valor nominal.")
        st.info("💡 **Interpretación:** La tasa de descuento es igual a la tasa cupón.")


def grafico_flujos(df_flujos):
    """Genera el gráfico de flujos de caja vs valor presente CON LEYENDAS"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=df_flujos['Flujo'],
        name='Flujo de Caja Nominal',
        marker_color='#3B82F6',
        hovertemplate='<b>Año:</b> %{x:.2f}<br><b>Flujo:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    fig.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=df_flujos['Valor Presente'],
        name='Valor Presente Descontado',
        marker_color='#10B981',
        hovertemplate='<b>Año:</b> %{x:.2f}<br><b>VP:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    fig.update_layout(
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

    return fig


def grafico_vp_acumulado(df_flujos, valor_nominal):
    """Genera el gráfico de valor presente acumulado CON LEYENDAS"""
    df_flujos_copy = df_flujos.copy()
    df_flujos_copy['VP Acumulado'] = df_flujos_copy['Valor Presente'].cumsum()

    fig = go.Figure()

    # Línea principal de VP Acumulado
    fig.add_trace(go.Scatter(
        x=df_flujos_copy['Año'],
        y=df_flujos_copy['VP Acumulado'],
        mode='lines+markers',
        name='VP Acumulado',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.2)',
        hovertemplate='<b>Año:</b> %{x:.2f}<br><b>VP Acum:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    # Línea de referencia del Valor Nominal (como trace para que aparezca en leyenda)
    fig.add_trace(go.Scatter(
        x=[df_flujos_copy['Año'].min(), df_flujos_copy['Año'].max()],
        y=[valor_nominal, valor_nominal],
        mode='lines',
        name='Valor Nominal',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='<b>Valor Nominal:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    fig.update_layout(
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


def resumen_bono(valor_nominal, tasa_cupon, tasa_cupon_periodica, frecuencia_bono,
                 cupon, plazo_bono, total_periodos_bono, tea_bono,
                 tasa_descuento_periodica, df_flujos, valor_presente_total):
    """Muestra el resumen completo del bono"""
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Valor Nominal:** {formato_moneda(valor_nominal)}")
        st.write(f"**Tasa Cupón (TEA):** {tasa_cupon}%")
        st.write(f"**Tasa Cupón Periódica:** {tasa_cupon_periodica * 100:.4f}%")
        st.write(f"**Frecuencia:** {frecuencia_bono}")
        st.write(f"**Cupón por Período:** {formato_moneda(cupon)}")

    with col2:
        st.write(f"**Plazo:** {plazo_bono} años ({total_periodos_bono} períodos)")
        st.write(f"**Tasa de Descuento (TEA):** {tea_bono}%")
        st.write(f"**Tasa de Descuento Periódica:** {tasa_descuento_periodica * 100:.4f}%")
        st.write(f"**Total de Flujos:** {formato_moneda(df_flujos['Flujo'].sum())}")
        st.write(f"**Valor Presente:** {formato_moneda(valor_presente_total)}")


def comparacion_escenarios(tasa_escenario1, tasa_escenario2, tea_bono,
                           valor_nominal, cupon, total_periodos_bono,
                           frecuencia_bono, convertir_tea_a_periodica):
    """Muestra la comparación de escenarios con diferentes tasas"""
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

    # Mostrar comparación
    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        st.metric(
            f"Escenario 1 ({tasa_escenario1}%)",
            formato_moneda(vp_esc1),
            delta=formato_moneda(vp_esc1 - valor_nominal)
        )

    with col_res2:
        st.metric(
            f"Actual ({tea_bono}%)",
            formato_moneda(vp_actual),
            delta=formato_moneda(vp_actual - valor_nominal)
        )

    with col_res3:
        st.metric(
            f"Escenario 2 ({tasa_escenario2}%)",
            formato_moneda(vp_esc2),
            delta=formato_moneda(vp_esc2 - valor_nominal)
        )

    return vp_esc1, vp_actual, vp_esc2


def grafico_sensibilidad(valor_nominal, cupon, total_periodos_bono,
                         frecuencia_bono, tea_bono, convertir_tea_a_periodica):
    """Genera el gráfico de análisis de sensibilidad CON LEYENDAS COMPLETAS"""
    from utils.utils import convertir_tea_a_periodica

    # Generar datos
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

    # Calcular valor actual
    tasa_actual_per = convertir_tea_a_periodica(tea_bono, frecuencia_bono)
    valor_actual = sum([
        (cupon if i < total_periodos_bono else cupon + valor_nominal) /
        ((1 + tasa_actual_per) ** i)
        for i in range(1, total_periodos_bono + 1)
    ])

    fig = go.Figure()

    # Línea principal del valor del bono
    fig.add_trace(go.Scatter(
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
    fig.add_trace(go.Scatter(
        x=[min(tasas_rango), max(tasas_rango)],
        y=[valor_nominal, valor_nominal],
        mode='lines',
        name='Valor Nominal (Par)',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='<b>Valor Nominal:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    # Línea de referencia de la Tasa Actual
    fig.add_trace(go.Scatter(
        x=[tea_bono, tea_bono],
        y=[min(valores_sensibilidad), max(valores_sensibilidad)],
        mode='lines',
        name=f'Tasa Actual ({tea_bono}%)',
        line=dict(color='green', width=2, dash='dot'),
        hovertemplate='<b>Tasa Actual:</b> %{x:.2f}%<extra></extra>',
        showlegend=True
    ))

    # Punto actual
    fig.add_trace(go.Scatter(
        x=[tea_bono],
        y=[valor_actual],
        mode='markers',
        name='Punto Actual',
        marker=dict(color='orange', size=12, symbol='star'),
        hovertemplate='<b>Tasa:</b> %{x:.2f}%<br><b>Valor:</b> $%{y:,.2f}<extra></extra>',
        showlegend=True
    ))

    fig.update_layout(
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

    return fig


def mostrar_resultados_completos(valor_nominal, tasa_cupon, frecuencia_bono,
                                 plazo_bono, tea_bono, df_flujos,
                                 valor_presente_total, cupon,
                                 tasa_cupon_periodica, tasa_descuento_periodica,
                                 num_periodos_bono):
    """
    Función principal que orquesta la visualización de todos los resultados
    """
    total_periodos_bono = plazo_bono * num_periodos_bono

    # Métricas principales
    st.divider()
    mostrar_metricas_bono(valor_presente_total, valor_nominal, cupon)

    # Interpretación
    st.divider()
    mostrar_interpretacion(valor_presente_total, valor_nominal, tea_bono, tasa_cupon)

    # Gráficos (NO se muestran aquí, se manejan en form_mod_c.py para incluir leyendas personalizadas)

    # Tabla de flujos
    st.divider()
    st.subheader("📋 Detalle de Flujos")
    tabla_flujos(df_flujos)

    # Resumen
    st.divider()
    st.subheader("📌 Resumen del Bono")
    resumen_bono(valor_nominal, tasa_cupon, tasa_cupon_periodica, frecuencia_bono,
                 cupon, plazo_bono, total_periodos_bono, tea_bono,
                 tasa_descuento_periodica, df_flujos, valor_presente_total)

    return total_periodos_bono