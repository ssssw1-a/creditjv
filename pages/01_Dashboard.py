"""
Dashboard - Centro de Comando
Vista general del sistema con KPIs y alertas
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from database import get_database
from utils import format_currency, format_number, format_estado, get_estado_color

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

# ==================== TÍTULO ====================

st.title("🏠 Dashboard")
st.markdown("Centro de Comando - Vista general del sistema")
st.markdown("---")

# ==================== INICIALIZAR BASE DE DATOS ====================

db = get_database()

# ==================== OBTENER DATOS ====================

resumen = db.get_resumen_cartera()
clientes_df = db.get_clientes()

# ==================== KPIs ====================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Clientes",
        value=format_number(resumen.get('total_clientes', 0))
    )

with col2:
    st.metric(
        label="Clientes Al Día",
        value=format_number(resumen.get('clientes_al_dia', 0)),
        delta=f"{resumen.get('clientes_al_dia', 0)}"
    )

with col3:
    st.metric(
        label="Clientes Pendientes",
        value=format_number(resumen.get('clientes_pendientes', 0))
    )

with col4:
    st.metric(
        label="Clientes Atrasados",
        value=format_number(resumen.get('clientes_atrasados', 0))
    )

st.markdown("---")

# ==================== MÉTRICAS FINANCIERAS ====================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; text-align: center;">
        <p style="color: #94a3b8; margin: 0;">Total por Cobrar</p>
        <h2 style="color: #ef4444; margin: 10px 0;">{}</h2>
    </div>
    """.format(format_currency(resumen.get('total_por_cobrar', 0))), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; text-align: center;">
        <p style="color: #94a3b8; margin: 0;">Total Cobrado</p>
        <h2 style="color: #22c55e; margin: 10px 0;">{}</h2>
    </div>
    """.format(format_currency(resumen.get('total_pagado', 0))), unsafe_allow_html=True)

with col3:
    deuda_total = resumen.get('total_deuda', 0)
    st.markdown("""
    <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; text-align: center;">
        <p style="color: #94a3b8; margin: 0;">Deuda Total</p>
        <h2 style="color: #14b8a6; margin: 10px 0;">{}</h2>
    </div>
    """.format(format_currency(deuda_total)), unsafe_allow_html=True)

st.markdown("---")

# ==================== GRÁFICOS ====================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribución de Clientes")
    
    if resumen.get('total_clientes', 0) > 0:
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Al Día', 'Pendientes', 'Atrasados'],
            values=[
                resumen.get('clientes_al_dia', 0),
                resumen.get('clientes_pendientes', 0),
                resumen.get('clientes_atrasados', 0)
            ],
            marker_colors=['#22c55e', '#f59e0b', '#ef4444'],
            hole=0.4
        )])
        
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc')
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No hay datos suficientes para mostrar el gráfico")

with col2:
    st.subheader("💰 Resumen Financiero")
    
    if deuda_total > 0:
        fig_bar = go.Figure(data=[
            go.Bar(
                name='Cobrado',
                x=['Finanzas'],
                y=[resumen.get('total_pagado', 0)],
                marker_color='#22c55e'
            ),
            go.Bar(
                name='Por Cobrar',
                x=['Finanzas'],
                y=[resumen.get('total_por_cobrar', 0)],
                marker_color='#ef4444'
            )
        ])
        
        fig_bar.update_layout(
            barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc'),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hay datos financieros para mostrar")

st.markdown("---")

# ==================== CLIENTES CON ATRASO ====================

st.subheader("⚠️ Clientes con Atraso")

clientes_atrasados = db.get_clientes_atrasados()

if not clientes_atrasados.empty:
    for _, cliente in clientes_atrasados.head(5).iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.markdown(f"**{cliente['nombre']}**")
            st.caption(f"📦 {cliente['producto']}")
        
        with col2:
            st.markdown(f"📞 {cliente['telefono']}")
        
        with col3:
            st.markdown(f"💰 **{format_currency(cliente['saldo_pendiente'])}**")
        
        with col4:
            if st.button("Ver", key=f"ver_{cliente['id']}"):
                st.session_state['cliente_seleccionado'] = cliente['id']
                st.switch_page("pages/02_Clientes.py")
        
        st.markdown("---")
else:
    st.success("🎉 No hay clientes con atrasos. ¡Excelente trabajo!")

# ==================== ACCIONES RÁPIDAS ====================

st.subheader("⚡ Acciones Rápidas")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ Nuevo Cliente", use_container_width=True):
        st.switch_page("pages/02_Clientes.py")

with col2:
    if st.button("💵 Registrar Pago", use_container_width=True):
        st.switch_page("pages/03_Pagos.py")

with col3:
    if st.button("📊 Ver Reportes", use_container_width=True):
        st.switch_page("pages/04_Reportes.py")
