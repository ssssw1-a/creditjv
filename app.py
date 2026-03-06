"""
Sistema de Cobranzas - Aplicación Principal (Streamlit)
Punto de entrada de la aplicación
"""

import streamlit as st
from utils import get_custom_css

# ==================== CONFIGURACIÓN DE PÁGINA ====================

st.set_page_config(
    page_title="Sistema de Cobranzas",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS PERSONALIZADO ====================

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ==================== PÁGINA PRINCIPAL (REDIRECCIÓN) ====================

# La navegación en Streamlit se maneja automáticamente con la carpeta pages/
# Esta página solo muestra un mensaje de bienvenida y redirige

st.title("💰 Sistema de Cobranzas")
st.markdown("---")

st.markdown("""
## Bienvenido al Sistema de Cobranzas

Esta aplicación te permite gestionar la cartera de clientes y pagos de tu negocio.

### 📋 Módulos disponibles:

- **🏠 Dashboard** - Vista general con KPIs y alertas
- **👥 Clientes** - Gestión completa de clientes (CRUD)
- **💵 Pagos** - Registro y seguimiento de pagos
- **📊 Reportes** - Generación de reportes y PDFs

### 🚀 Empezar:

Selecciona una opción del menú lateral para navegar entre los diferentes módulos.
""")

st.markdown("---")

# Botones de navegación rápida
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("pages/01_Dashboard.py")

with col2:
    if st.button("👥 Clientes", use_container_width=True):
        st.switch_page("pages/02_Clientes.py")

with col3:
    if st.button("💵 Pagos", use_container_width=True):
        st.switch_page("pages/03_Pagos.py")

with col4:
    if st.button("📊 Reportes", use_container_width=True):
        st.switch_page("pages/04_Reportes.py")

st.markdown("---")

# Información del sistema
st.caption("Sistema de Cobranzas v1.0 - Desarrollado con Streamlit")
