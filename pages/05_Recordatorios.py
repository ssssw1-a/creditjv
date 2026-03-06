"""
Recordatorios - Sistema de alertas y recordatorios
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_database
from utils import format_date, format_tipo_recordatorio

st.set_page_config(page_title="Recordatorios", page_icon="🔔", layout="wide")

# ==================== TÍTULO ====================

st.title("🔔 Recordatorios")
st.markdown("Gestión de alertas y recordatorios de pagos")
st.markdown("---")

# ==================== INICIALIZAR BASE DE DATOS ====================

db = get_database()

# ==================== TABS ====================

tab_lista, tab_nuevo = st.tabs(["📋 Lista de Recordatorios", "➕ Nuevo Recordatorio"])

# ==================== TAB: LISTA DE RECORDATORIOS ====================

with tab_lista:
    # Filtros
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todos", "Pendiente", "Enviado"]
        )
    
    with col2:
        filtro_tipo = st.selectbox(
            "Filtrar por tipo",
            ["Todos", "Mensual", "Fecha de Vencimiento", "Seguimiento"]
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Obtener recordatorios
    recordatorios_df = db.get_recordatorios()
    
    # Aplicar filtros
    if filtro_estado != "Todos":
        estado_map = {"Pendiente": "pendiente", "Enviado": "enviado"}
        recordatorios_df = recordatorios_df[recordatorios_df['estado'] == estado_map.get(filtro_estado, "")]
    
    if filtro_tipo != "Todos":
        tipo_map = {"Mensual": "mensual", "Fecha de Vencimiento": "fecha_vencimiento", "Seguimiento": "seguimiento"}
        recordatorios_df = recordatorios_df[recordatorios_df['tipo'] == tipo_map.get(filtro_tipo, "")]
    
    # Estadísticas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total", len(recordatorios_df))
    
    with col2:
        pendientes = len(recordatorios_df[recordatorios_df['estado'] == 'pendiente'])
        st.metric("Pendientes", pendientes)
    
    with col3:
        enviados = len(recordatorios_df[recordatorios_df['estado'] == 'enviado'])
        st.metric("Enviados", enviados)
    
    st.markdown("---")
    
    # Mostrar recordatorios
    if not recordatorios_df.empty:
        # Preparar datos
        display_df = recordatorios_df[['cliente_nombre', 'tipo', 'fecha_programada', 'mensaje', 'estado']].copy()
        
        display_df['fecha_programada'] = display_df['fecha_programada'].apply(format_date)
        display_df['tipo'] = display_df['tipo'].apply(format_tipo_recordatorio)
        
        # Marcar vencidos
        hoy = datetime.now().date()
        display_df['estado_display'] = recordatorios_df.apply(
            lambda x: '⚠️ Vencido' if x['estado'] == 'pendiente' and 
            datetime.fromisoformat(x['fecha_programada']).date() < hoy 
            else ('⏳ Pendiente' if x['estado'] == 'pendiente' else '✅ Enviado'),
            axis=1
        )
        
        display_df.columns = ['Cliente', 'Tipo', 'Fecha Programada', 'Mensaje', 'Estado Original', 'Estado']
        display_df = display_df.drop('Estado Original', axis=1)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Acciones
        st.markdown("### Acciones")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            recordatorio_seleccionado = st.selectbox(
                "Seleccionar recordatorio",
                options=recordatorios_df['id'].tolist(),
                format_func=lambda x: f"{recordatorios_df[recordatorios_df['id'] == x]['cliente_nombre'].iloc[0]} - {format_tipo_recordatorio(recordatorios_df[recordatorios_df['id'] == x]['tipo'].iloc[0])}"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            rec_estado = recordatorios_df[recordatorios_df['id'] == recordatorio_seleccionado]['estado'].iloc[0] if recordatorio_seleccionado else None
            
            if rec_estado == 'pendiente':
                if st.button("✅ Marcar Enviado", use_container_width=True):
                    db.marcar_recordatorio_enviado(recordatorio_seleccionado)
                    st.success("Recordatorio marcado como enviado")
                    st.rerun()
            
            if st.button("🗑️ Eliminar", use_container_width=True):
                if st.checkbox("Confirmar eliminación"):
                    db.eliminar_recordatorio(recordatorio_seleccionado)
                    st.success("Recordatorio eliminado")
                    st.rerun()
    else:
        st.info("No hay recordatorios registrados")

# ==================== TAB: NUEVO RECORDATORIO ====================

with tab_nuevo:
    st.markdown("### Crear Nuevo Recordatorio")
    
    clientes_df = db.get_clientes()
    
    if not clientes_df.empty:
        with st.form("form_nuevo_recordatorio"):
            col1, col2 = st.columns(2)
            
            with col1:
                cliente_id = st.selectbox(
                    "Cliente *",
                    options=clientes_df['id'].tolist(),
                    format_func=lambda x: f"{clientes_df[clientes_df['id'] == x]['nombre'].iloc[0]}"
                )
                
                tipo = st.selectbox(
                    "Tipo de Recordatorio *",
                    ["mensual", "fecha_vencimiento", "seguimiento"],
                    format_func=lambda x: {"mensual": "📅 Mensual", "fecha_vencimiento": "⏰ Fecha de Vencimiento", "seguimiento": "📋 Seguimiento"}[x]
                )
            
            with col2:
                # Fecha por defecto: mañana
                fecha_default = datetime.now() + timedelta(days=1)
                fecha_programada = st.date_input(
                    "Fecha Programada *",
                    value=fecha_default,
                    min_value=datetime.now().date()
                )
                
                mensaje = st.text_area(
                    "Mensaje *",
                    placeholder="Escribe el mensaje del recordatorio...",
                    value="Recordatorio de pago pendiente"
                )
            
            submitted = st.form_submit_button("💾 Crear Recordatorio", use_container_width=True)
            
            if submitted:
                # Validaciones
                errores = []
                
                if not cliente_id:
                    errores.append("Debes seleccionar un cliente")
                
                if not mensaje or len(mensaje) < 5:
                    errores.append("El mensaje debe tener al menos 5 caracteres")
                
                if errores:
                    for error in errores:
                        st.error(error)
                else:
                    try:
                        recordatorio_id = db.crear_recordatorio(
                            cliente_id=cliente_id,
                            tipo=tipo,
                            fecha_programada=fecha_programada.isoformat(),
                            mensaje=mensaje
                        )
                        
                        st.success("✅ Recordatorio creado correctamente!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error al crear recordatorio: {str(e)}")
    else:
        st.warning("⚠️ No hay clientes registrados. Primero debes registrar un cliente.")
        
        if st.button("➕ Ir a Clientes", use_container_width=True):
            st.switch_page("pages/02_Clientes.py")
