"""
Pagos - Libro Mayor de Pagos
Registro y seguimiento de pagos
"""

import streamlit as st
import pandas as pd
from database import get_database
from utils import format_currency, format_tipo_pago, format_metodo_pago, format_datetime
from pdf_generator import generar_recibo_pago

st.set_page_config(page_title="Pagos", page_icon="💵", layout="wide")

# ==================== TÍTULO ====================

st.title("💵 Libro de Pagos")
st.markdown("Registro y seguimiento de todos los pagos")
st.markdown("---")

# ==================== INICIALIZAR BASE DE DATOS ====================

db = get_database()

# ==================== TABS ====================

tab_lista, tab_nuevo = st.tabs(["📋 Historial de Pagos", "➕ Registrar Pago"])

# ==================== TAB: HISTORIAL DE PAGOS ====================

with tab_lista:
    # Filtros
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        filtro_tipo = st.selectbox(
            "Filtrar por tipo",
            ["Todos", "Pago Inicial", "Cuota", "Abono", "Liquidación"]
        )
    
    with col2:
        filtro_metodo = st.selectbox(
            "Filtrar por método",
            ["Todos", "Efectivo", "Transferencia", "Depósito", "Cheque", "Otro"]
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Obtener pagos
    pagos_df = db.get_pagos()
    
    # Aplicar filtros
    if filtro_tipo != "Todos":
        tipo_map = {"Pago Inicial": "inicial", "Cuota": "cuota", "Abono": "abono", "Liquidación": "liquidacion"}
        pagos_df = pagos_df[pagos_df['tipo'] == tipo_map.get(filtro_tipo, "")]
    
    if filtro_metodo != "Todos":
        metodo_map = {"Efectivo": "efectivo", "Transferencia": "transferencia", 
                     "Depósito": "deposito", "Cheque": "cheque", "Otro": "otro"}
        pagos_df = pagos_df[pagos_df['metodo'] == metodo_map.get(filtro_metodo, "")]
    
    # Mostrar totales
    col1, col2 = st.columns(2)
    
    with col1:
        total_recaudado = pagos_df['monto'].sum() if not pagos_df.empty else 0
        st.markdown(f"""
        <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; text-align: center;">
            <p style="color: #94a3b8; margin: 0;">Total Recaudado</p>
            <h3 style="color: #22c55e; margin: 5px 0;">{format_currency(total_recaudado)}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; text-align: center;">
            <p style="color: #94a3b8; margin: 0;">Total de Pagos</p>
            <h3 style="color: #14b8a6; margin: 5px 0;">{len(pagos_df)}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mostrar tabla de pagos
    if not pagos_df.empty:
        # Preparar datos para mostrar
        display_df = pagos_df[['cliente_nombre', 'fecha', 'monto', 'tipo', 'metodo', 'notas']].copy()
        
        display_df['fecha'] = display_df['fecha'].apply(format_datetime)
        display_df['monto'] = display_df['monto'].apply(format_currency)
        display_df['tipo'] = display_df['tipo'].apply(format_tipo_pago)
        display_df['metodo'] = display_df['metodo'].apply(format_metodo_pago)
        
        display_df.columns = ['Cliente', 'Fecha', 'Monto', 'Tipo', 'Método', 'Notas']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Acciones
        st.markdown("### Acciones")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            pago_seleccionado = st.selectbox(
                "Seleccionar pago",
                options=pagos_df['id'].tolist(),
                format_func=lambda x: f"{pagos_df[pagos_df['id'] == x]['cliente_nombre'].iloc[0]} - {format_currency(pagos_df[pagos_df['id'] == x]['monto'].iloc[0])}"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("📄 Recibo", use_container_width=True):
                    if pago_seleccionado:
                        pago_row = pagos_df[pagos_df['id'] == pago_seleccionado].iloc[0]
                        cliente = db.get_cliente_by_id(pago_row['cliente_id'])
                        
                        if cliente:
                            pdf_buffer = generar_recibo_pago(cliente, pago_row.to_dict())
                            st.download_button(
                                label="⬇️ Descargar",
                                data=pdf_buffer,
                                file_name=f"recibo_{pago_seleccionado[-8:]}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
            
            with col_btn2:
                if st.button("🗑️ Eliminar", use_container_width=True):
                    if pago_seleccionado:
                        pago_monto = pagos_df[pagos_df['id'] == pago_seleccionado]['monto'].iloc[0]
                        pago_cliente = pagos_df[pagos_df['id'] == pago_seleccionado]['cliente_nombre'].iloc[0]
                        
                        if st.checkbox(f"Confirmar eliminación de {format_currency(pago_monto)}"):
                            db.eliminar_pago(pago_seleccionado)
                            st.success("Pago eliminado correctamente")
                            st.rerun()
    else:
        st.info("No hay pagos registrados. ¡Registra tu primer pago!")

# ==================== TAB: REGISTRAR PAGO ====================

with tab_nuevo:
    st.markdown("### Registrar Nuevo Pago")
    
    # Obtener clientes
    clientes_df = db.get_clientes()
    
    if not clientes_df.empty:
        with st.form("form_nuevo_pago"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Selector de cliente
                cliente_id = st.selectbox(
                    "Cliente *",
                    options=clientes_df['id'].tolist(),
                    format_func=lambda x: f"{clientes_df[clientes_df['id'] == x]['nombre'].iloc[0]} (Saldo: {format_currency(clientes_df[clientes_df['id'] == x]['saldo_pendiente'].iloc[0])})"
                )
                
                # Mostrar información del cliente seleccionado
                if cliente_id:
                    cliente_data = db.get_cliente_by_id(cliente_id)
                    if cliente_data:
                        st.info(f"""
                        **Deuda Total:** {format_currency(cliente_data['total_deuda'])}  
                        **Total Pagado:** {format_currency(cliente_data['total_pagado'])}  
                        **Saldo Pendiente:** {format_currency(cliente_data['saldo_pendiente'])}
                        """)
                
                monto = st.number_input(
                    "Monto *", 
                    min_value=0.0, 
                    value=0.0, 
                    step=50.0,
                    help="Monto del pago a registrar"
                )
            
            with col2:
                tipo = st.selectbox(
                    "Tipo de Pago *",
                    ["inicial", "cuota", "abono", "liquidacion"],
                    format_func=lambda x: {"inicial": "Pago Inicial", "cuota": "Cuota", "abono": "Abono", "liquidacion": "Liquidación"}[x]
                )
                
                metodo = st.selectbox(
                    "Método de Pago *",
                    ["efectivo", "transferencia", "deposito", "cheque", "otro"],
                    format_func=lambda x: {"efectivo": "💵 Efectivo", "transferencia": "🏦 Transferencia", "deposito": "📥 Depósito", "cheque": "📝 Cheque", "otro": "📋 Otro"}[x]
                )
                
                notas = st.text_area("Notas (opcional)", placeholder="Información adicional sobre el pago...")
            
            # Calcular saldo restante
            if cliente_id and monto > 0:
                cliente_data = db.get_cliente_by_id(cliente_id)
                if cliente_data:
                    saldo_restante = max(0, cliente_data['saldo_pendiente'] - monto)
                    
                    if monto > cliente_data['saldo_pendiente']:
                        st.warning(f"⚠️ El monto excede el saldo pendiente ({format_currency(cliente_data['saldo_pendiente'])})")
                    else:
                        st.success(f"✅ Saldo después del pago: {format_currency(saldo_restante)}")
            
            submitted = st.form_submit_button("💾 Registrar Pago", use_container_width=True)
            
            if submitted:
                # Validaciones
                errores = []
                
                if not cliente_id:
                    errores.append("Debes seleccionar un cliente")
                
                if monto <= 0:
                    errores.append("El monto debe ser mayor a 0")
                
                if cliente_id:
                    cliente_data = db.get_cliente_by_id(cliente_id)
                    if cliente_data and monto > cliente_data['saldo_pendiente']:
                        errores.append(f"El monto no puede exceder el saldo pendiente ({format_currency(cliente_data['saldo_pendiente'])})")
                
                if errores:
                    for error in errores:
                        st.error(error)
                else:
                    try:
                        pago_id = db.registrar_pago(
                            cliente_id=cliente_id,
                            monto=monto,
                            tipo=tipo,
                            metodo=metodo,
                            notas=notas
                        )
                        
                        st.success(f"✅ Pago de {format_currency(monto)} registrado correctamente!")
                        
                        # Ofrecer descargar recibo
                        cliente = db.get_cliente_by_id(cliente_id)
                        pago_data = {
                            'id': pago_id,
                            'cliente_id': cliente_id,
                            'fecha': pd.Timestamp.now().isoformat(),
                            'monto': monto,
                            'tipo': tipo,
                            'metodo': metodo,
                            'notas': notas
                        }
                        
                        pdf_buffer = generar_recibo_pago(cliente, pago_data)
                        st.download_button(
                            label="📄 Descargar Recibo",
                            data=pdf_buffer,
                            file_name=f"recibo_{pago_id[-8:]}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"Error al registrar pago: {str(e)}")
    else:
        st.warning("⚠️ No hay clientes registrados. Primero debes registrar un cliente.")
        
        if st.button("➕ Ir a Clientes", use_container_width=True):
            st.switch_page("pages/02_Clientes.py")
