"""
Reportes - Generación de reportes y estadísticas
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from database import get_database
from utils import format_currency, format_number
from pdf_generator import generar_reporte_cartera, generar_estado_cuenta

st.set_page_config(page_title="Reportes", page_icon="📊", layout="wide")

# ==================== TÍTULO ====================

st.title("📊 Reportes y Estadísticas")
st.markdown("Análisis y generación de documentos")
st.markdown("---")

# ==================== INICIALIZAR BASE DE DATOS ====================

db = get_database()

# ==================== TABS ====================

tab_estadisticas, tab_pdfs, tab_datos = st.tabs(["📈 Estadísticas", "📄 Documentos PDF", "💾 Gestión de Datos"])

# ==================== TAB: ESTADÍSTICAS ====================

with tab_estadisticas:
    # Obtener datos
    resumen = db.get_resumen_cartera()
    clientes_df = db.get_clientes()
    pagos_df = db.get_pagos()
    
    # Progreso global
    if resumen.get('total_deuda', 0) > 0:
        progreso = (resumen.get('total_pagado', 0) / resumen.get('total_deuda', 0)) * 100
    else:
        progreso = 0
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Progreso de Cobranza")
        
        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progreso,
            number={'suffix': '%'},
            title={'text': "Cobrado"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#14b8a6"},
                'bgcolor': "#1e293b",
                'borderwidth': 2,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, 50], 'color': "#fee2e2"},
                    {'range': [50, 75], 'color': "#fef3c7"},
                    {'range': [75, 100], 'color': "#dcfce7"}
                ],
                'threshold': {
                    'line': {'color': "#22c55e", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc')
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        st.markdown("### Distribución Financiera")
        
        # Gráfico de barras apiladas
        fig_bar = go.Figure(data=[
            go.Bar(name='Cobrado', x=['Total'], y=[resumen.get('total_pagado', 0)], marker_color='#22c55e'),
            go.Bar(name='Por Cobrar', x=['Total'], y=[resumen.get('total_por_cobrar', 0)], marker_color='#ef4444')
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
    
    st.markdown("---")
    
    # Gráfico de pagos por mes
    if not pagos_df.empty:
        st.markdown("### Pagos por Período")
        
        # Convertir fechas y agrupar
        pagos_df['fecha'] = pd.to_datetime(pagos_df['fecha'])
        pagos_df['mes'] = pagos_df['fecha'].dt.to_period('M')
        
        pagos_por_mes = pagos_df.groupby('mes')['monto'].sum().reset_index()
        pagos_por_mes['mes_str'] = pagos_por_mes['mes'].astype(str)
        
        fig_line = px.line(
            pagos_por_mes,
            x='mes_str',
            y='monto',
            markers=True,
            title="Evolución de Pagos"
        )
        
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc'),
            xaxis_title="Mes",
            yaxis_title="Monto ($)"
        )
        
        fig_line.update_traces(line_color='#14b8a6', marker_color='#14b8a6')
        
        st.plotly_chart(fig_line, use_container_width=True)

# ==================== TAB: DOCUMENTOS PDF ====================

with tab_pdfs:
    st.markdown("### Generar Documentos PDF")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Reporte de Cartera")
        st.markdown("Genera un reporte completo con todos los clientes y su estado financiero.")
        
        if st.button("Generar Reporte de Cartera", use_container_width=True):
            with st.spinner("Generando PDF..."):
                try:
                    resumen = db.get_resumen_cartera()
                    clientes_df = db.get_clientes()
                    
                    pdf_buffer = generar_reporte_cartera(resumen, clientes_df)
                    
                    st.download_button(
                        label="⬇️ Descargar Reporte",
                        data=pdf_buffer,
                        file_name=f"reporte_cartera_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    st.success("✅ Reporte generado correctamente!")
                except Exception as e:
                    st.error(f"Error al generar reporte: {str(e)}")
    
    with col2:
        st.markdown("#### 📄 Estado de Cuenta")
        st.markdown("Genera un estado de cuenta individual para un cliente específico.")
        
        clientes_df = db.get_clientes()
        
        if not clientes_df.empty:
            cliente_seleccionado = st.selectbox(
                "Seleccionar cliente",
                options=clientes_df['id'].tolist(),
                format_func=lambda x: clientes_df[clientes_df['id'] == x]['nombre'].iloc[0]
            )
            
            if st.button("Generar Estado de Cuenta", use_container_width=True):
                with st.spinner("Generando PDF..."):
                    try:
                        cliente = db.get_cliente_by_id(cliente_seleccionado)
                        pagos = db.get_pagos(cliente_seleccionado)
                        
                        pdf_buffer = generar_estado_cuenta(cliente, pagos.to_dict('records'))
                        
                        st.download_button(
                            label="⬇️ Descargar Estado de Cuenta",
                            data=pdf_buffer,
                            file_name=f"estado_cuenta_{cliente['nombre'].replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        st.success("✅ Estado de cuenta generado correctamente!")
                    except Exception as e:
                        st.error(f"Error al generar estado de cuenta: {str(e)}")
        else:
            st.info("No hay clientes registrados")

# ==================== TAB: GESTIÓN DE DATOS ====================

with tab_datos:
    st.markdown("### 💾 Gestión de Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📤 Exportar Datos")
        st.markdown("Exporta todos los datos del sistema para crear una copia de seguridad.")
        
        if st.button("Exportar Datos (JSON)", use_container_width=True):
            with st.spinner("Exportando datos..."):
                try:
                    datos = db.exportar_datos()
                    json_str = json.dumps(datos, indent=2, default=str)
                    
                    st.download_button(
                        label="⬇️ Descargar Backup",
                        data=json_str,
                        file_name=f"backup_cobranzas_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                    
                    st.success("✅ Datos exportados correctamente!")
                except Exception as e:
                    st.error(f"Error al exportar datos: {str(e)}")
    
    with col2:
        st.markdown("#### 📥 Importar Datos")
        st.markdown("Importa datos desde un archivo de backup JSON.")
        
        archivo_subido = st.file_uploader("Seleccionar archivo JSON", type=['json'])
        
        if archivo_subido is not None:
            if st.button("Importar Datos", use_container_width=True):
                with st.spinner("Importando datos..."):
                    try:
                        contenido = json.load(archivo_subido)
                        
                        # Aquí iría la lógica de importación
                        # Por seguridad, mostramos solo un mensaje
                        st.info("Función de importación: Procesar el archivo JSON y restaurar los datos en la base de datos.")
                        st.json(contenido)
                        
                    except Exception as e:
                        st.error(f"Error al importar datos: {str(e)}")
    
    st.markdown("---")
    
    # Información del sistema
    st.markdown("### ℹ️ Información del Sistema")
    
    resumen = db.get_resumen_cartera()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Clientes", resumen.get('total_clientes', 0))
    
    with col2:
        st.metric("Total Pagos", len(db.get_pagos()))
    
    with col3:
        st.metric("Total Recordatorios", len(db.get_recordatorios()))
