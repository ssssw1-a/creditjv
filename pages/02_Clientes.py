"""
Clientes - Gestión de Clientes (CRUD)
"""

import streamlit as st
import pandas as pd
from database import get_database
from utils import format_currency, format_estado, get_estado_color, validate_phone

st.set_page_config(page_title="Clientes", page_icon="👥", layout="wide")

# ==================== TÍTULO ====================

st.title("👥 Gestión de Clientes")
st.markdown("Administra tus clientes y su información")
st.markdown("---")

# ==================== INICIALIZAR BASE DE DATOS ====================

db = get_database()

# ==================== TABS ====================

tab_lista, tab_nuevo, tab_editar = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente", "✏️ Editar Cliente"])

# ==================== TAB: LISTA DE CLIENTES ====================

with tab_lista:
    # Filtros
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        busqueda = st.text_input("🔍 Buscar cliente", placeholder="Nombre, teléfono o producto...")
    
    with col2:
        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todos", "Al Día", "Pendiente", "Atrasado"],
            index=0
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Obtener clientes
    clientes_df = db.get_clientes()
    
    # Aplicar filtros
    if busqueda:
        clientes_df = clientes_df[
            clientes_df['nombre'].str.contains(busqueda, case=False, na=False) |
            clientes_df['telefono'].str.contains(busqueda, case=False, na=False) |
            clientes_df['producto'].str.contains(busqueda, case=False, na=False)
        ]
    
    if filtro_estado != "Todos":
        estado_map = {"Al Día": "al_dia", "Pendiente": "pendiente", "Atrasado": "atrasado"}
        clientes_df = clientes_df[clientes_df['estado'] == estado_map.get(filtro_estado, "")]
    
    # Mostrar estadísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", len(clientes_df))
    with col2:
        st.metric("Al Día", len(clientes_df[clientes_df['estado'] == 'al_dia']))
    with col3:
        st.metric("Pendientes", len(clientes_df[clientes_df['estado'] == 'pendiente']))
    with col4:
        st.metric("Atrasados", len(clientes_df[clientes_df['estado'] == 'atrasado']))
    
    st.markdown("---")
    
    # Mostrar tabla de clientes
    if not clientes_df.empty:
        # Preparar datos para mostrar
        display_df = clientes_df[['nombre', 'telefono', 'producto', 'total_deuda', 
                                   'total_pagado', 'saldo_pendiente', 'estado']].copy()
        
        display_df['total_deuda'] = display_df['total_deuda'].apply(format_currency)
        display_df['total_pagado'] = display_df['total_pagado'].apply(format_currency)
        display_df['saldo_pendiente'] = display_df['saldo_pendiente'].apply(format_currency)
        display_df['estado'] = display_df['estado'].apply(format_estado)
        
        display_df.columns = ['Nombre', 'Teléfono', 'Producto', 'Deuda Total', 
                             'Total Pagado', 'Saldo', 'Estado']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Acciones por cliente
        st.markdown("### Acciones")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            cliente_seleccionado = st.selectbox(
                "Seleccionar cliente",
                options=clientes_df['id'].tolist(),
                format_func=lambda x: clientes_df[clientes_df['id'] == x]['nombre'].iloc[0]
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Eliminar", use_container_width=True):
                if cliente_seleccionado:
                    cliente_nombre = clientes_df[clientes_df['id'] == cliente_seleccionado]['nombre'].iloc[0]
                    
                    # Confirmación
                    if st.checkbox(f"Confirmar eliminación de {cliente_nombre}"):
                        db.eliminar_cliente(cliente_seleccionado)
                        st.success(f"Cliente '{cliente_nombre}' eliminado correctamente")
                        st.rerun()
    else:
        st.info("No hay clientes registrados. ¡Agrega tu primer cliente!")

# ==================== TAB: NUEVO CLIENTE ====================

with tab_nuevo:
    st.markdown("### Registrar Nuevo Cliente")
    
    with st.form("form_nuevo_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre completo *", placeholder="Ej: Juan Pérez García")
            telefono = st.text_input("Teléfono *", placeholder="Ej: 5512345678")
            direccion = st.text_input("Dirección *", placeholder="Ej: Calle Principal #123")
            email = st.text_input("Email (opcional)", placeholder="Ej: cliente@email.com")
        
        with col2:
            producto = st.text_input("Producto *", placeholder="Ej: Refrigerador LG")
            total_deuda = st.number_input("Deuda Total *", min_value=0.0, value=0.0, step=100.0)
            notas = st.text_area("Notas (opcional)", placeholder="Información adicional...")
        
        submitted = st.form_submit_button("💾 Guardar Cliente", use_container_width=True)
        
        if submitted:
            # Validaciones
            errores = []
            
            if not nombre or len(nombre) < 3:
                errores.append("El nombre debe tener al menos 3 caracteres")
            
            if not telefono or len(telefono) < 8:
                errores.append("El teléfono debe tener al menos 8 dígitos")
            
            if not direccion or len(direccion) < 5:
                errores.append("La dirección debe tener al menos 5 caracteres")
            
            if not producto or len(producto) < 2:
                errores.append("El producto debe tener al menos 2 caracteres")
            
            if errores:
                for error in errores:
                    st.error(error)
            else:
                try:
                    cliente_id = db.crear_cliente(
                        nombre=nombre,
                        telefono=telefono,
                        direccion=direccion,
                        email=email,
                        total_deuda=total_deuda,
                        producto=producto,
                        notas=notas
                    )
                    st.success(f"✅ Cliente '{nombre}' registrado correctamente!")
                    
                    # Limpiar formulario (recargar página)
                    if st.button("🔄 Agregar otro cliente"):
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error al registrar cliente: {str(e)}")

# ==================== TAB: EDITAR CLIENTE ====================

with tab_editar:
    st.markdown("### Editar Cliente Existente")
    
    clientes_df = db.get_clientes()
    
    if not clientes_df.empty:
        cliente_editar = st.selectbox(
            "Seleccionar cliente a editar",
            options=clientes_df['id'].tolist(),
            format_func=lambda x: f"{clientes_df[clientes_df['id'] == x]['nombre'].iloc[0]} - {clientes_df[clientes_df['id'] == x]['producto'].iloc[0]}"
        )
        
        if cliente_editar:
            cliente_data = db.get_cliente_by_id(cliente_editar)
            
            if cliente_data:
                with st.form("form_editar_cliente"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nombre_edit = st.text_input("Nombre", value=cliente_data['nombre'])
                        telefono_edit = st.text_input("Teléfono", value=cliente_data['telefono'])
                        direccion_edit = st.text_input("Dirección", value=cliente_data['direccion'])
                        email_edit = st.text_input("Email", value=cliente_data['email'] or "")
                    
                    with col2:
                        producto_edit = st.text_input("Producto", value=cliente_data['producto'])
                        notas_edit = st.text_area("Notas", value=cliente_data['notas'] or "")
                    
                    submitted_edit = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
                    
                    if submitted_edit:
                        try:
                            db.actualizar_cliente(
                                cliente_editar,
                                nombre=nombre_edit,
                                telefono=telefono_edit,
                                direccion=direccion_edit,
                                email=email_edit,
                                producto=producto_edit,
                                notas=notas_edit
                            )
                            st.success("✅ Cliente actualizado correctamente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar cliente: {str(e)}")
    else:
        st.info("No hay clientes para editar")
