"""
Utilidades - Sistema de Cobranzas (Streamlit)
Funciones de formateo y utilidades
"""

from datetime import datetime
from typing import Optional

# ==================== FORMATEO DE MONEDA ====================

def format_currency(amount: float, symbol: str = "$") -> str:
    """Formatea un número como moneda"""
    if amount is None:
        amount = 0
    return f"{symbol}{amount:,.2f}"

# ==================== FORMATEO DE FECHAS ====================

def format_date(date_str: str, input_format: str = None) -> str:
    """Formatea una fecha a formato legible"""
    if not date_str:
        return "N/A"
    
    try:
        if input_format:
            dt = datetime.strptime(date_str, input_format)
        else:
            # Intentar formato ISO
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y")
    except:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y")
        except:
            return date_str

def format_datetime(date_str: str) -> str:
    """Formatea fecha y hora"""
    if not date_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return date_str

# ==================== FORMATEO DE NÚMEROS ====================

def format_number(num: int) -> str:
    """Formatea un número con separadores de miles"""
    return f"{num:,}"

# ==================== FORMATEO DE ESTADOS ====================

def format_estado(estado: str) -> str:
    """Formatea el estado de un cliente"""
    estados = {
        'al_dia': 'Al Día ✅',
        'pendiente': 'Pendiente ⏳',
        'atrasado': 'Atrasado ⚠️',
        'cancelado': 'Cancelado ❌'
    }
    return estados.get(estado, estado)

def format_tipo_pago(tipo: str) -> str:
    """Formatea el tipo de pago"""
    tipos = {
        'inicial': 'Pago Inicial',
        'cuota': 'Cuota',
        'abono': 'Abono',
        'liquidacion': 'Liquidación'
    }
    return tipos.get(tipo, tipo)

def format_metodo_pago(metodo: str) -> str:
    """Formatea el método de pago"""
    metodos = {
        'efectivo': '💵 Efectivo',
        'transferencia': '🏦 Transferencia',
        'deposito': '📥 Depósito',
        'cheque': '📝 Cheque',
        'otro': '📋 Otro'
    }
    return metodos.get(metodo, metodo)

def format_tipo_recordatorio(tipo: str) -> str:
    """Formatea el tipo de recordatorio"""
    tipos = {
        'mensual': '📅 Mensual',
        'fecha_vencimiento': '⏰ Fecha de Vencimiento',
        'seguimiento': '📋 Seguimiento'
    }
    return tipos.get(tipo, tipo)

# ==================== COLORES POR ESTADO ====================

def get_estado_color(estado: str) -> str:
    """Retorna el color asociado a un estado"""
    colores = {
        'al_dia': '#22c55e',      # verde
        'pendiente': '#f59e0b',   # amarillo
        'atrasado': '#ef4444',    # rojo
        'enviado': '#22c55e',     # verde
        'pendiente_rec': '#f59e0b' # amarillo
    }
    return colores.get(estado, '#94a3b8')

# ==================== VALIDACIÓN ====================

def validate_email(email: str) -> bool:
    """Valida un correo electrónico"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) if email else True

def validate_phone(phone: str) -> bool:
    """Valida un número de teléfono"""
    # Remover espacios y guiones
    cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    return len(cleaned) >= 8 and cleaned.isdigit()

# ==================== CÁLCULOS ====================

def calcular_progreso(total_pagado: float, total_deuda: float) -> float:
    """Calcula el porcentaje de progreso de pago"""
    if total_deuda <= 0:
        return 100
    return min(100, (total_pagado / total_deuda) * 100)

# ==================== CSS PERSONALIZADO ====================

def get_custom_css() -> str:
    """Retorna CSS personalizado para la aplicación"""
    return """
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Cards */
    .css-1r6slb0, .css-1y4p8pa {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #334155;
    }
    
    /* Botones */
    .stButton > button {
        background-color: #14b8a6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #0d9488;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    /* Tablas */
    .dataframe {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }
    
    .dataframe th {
        background-color: #334155 !important;
        color: #f8fafc !important;
    }
    
    .dataframe td {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }
    
    /* Métricas */
    .css-1xarl3l {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #334155;
    }
    
    /* Sidebar */
    .css-1cypcdb {
        background-color: #1e293b;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }
    
    /* Texto */
    p, span, label {
        color: #cbd5e1 !important;
    }
    
    /* Alertas */
    .stAlert {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #cbd5e1;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #14b8a6;
        color: white;
    }
    </style>
    """
