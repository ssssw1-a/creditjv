# Sistema de Cobranzas - Streamlit

Sistema de gestión de cobranzas para pequeñas empresas, desarrollado con Python y Streamlit.

## Características

- **Gestión de Clientes**: CRUD completo de clientes con información personal y financiera
- **Registro de Pagos**: Seguimiento de pagos con cálculo automático de saldos
- **Dashboard**: KPIs en tiempo real con gráficos interactivos
- **Reportes PDF**: Generación de recibos, estados de cuenta y reportes de cartera
- **Dark Mode**: Interfaz moderna con tema oscuro
- **Persistencia**: Base de datos SQLite para almacenamiento local

## Estructura del Proyecto

```
sistema_cobranzas_streamlit/
├── app.py                      # Punto de entrada de la aplicación
├── database.py                 # Módulo de base de datos SQLite
├── utils.py                    # Utilidades y formateadores
├── pdf_generator.py            # Generación de PDFs con ReportLab
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Este archivo
├── .streamlit/
│   └── config.toml            # Configuración de tema (Dark Mode)
└── pages/
    ├── 01_Dashboard.py        # Dashboard con KPIs
    ├── 02_Clientes.py         # Gestión de clientes
    ├── 03_Pagos.py            # Libro de pagos
    └── 04_Reportes.py         # Reportes y estadísticas
```

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd sistema_cobranzas_streamlit
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## Funcionalidades

### Dashboard
- KPIs principales: Total de clientes, al día, pendientes, atrasados
- Métricas financieras: Por cobrar, cobrado, deuda total
- Gráficos de distribución y progreso
- Alertas de clientes con atraso

### Clientes
- Lista completa con filtros y búsqueda
- Crear nuevos clientes
- Editar información existente
- Eliminar clientes
- Ver estado financiero

### Pagos
- Historial completo de pagos
- Filtros por tipo y método
- Registrar nuevos pagos
- Generar recibos PDF
- Eliminar pagos (con recálculo de saldos)

### Reportes
- Estadísticas visuales
- Reporte de cartera (PDF)
- Estado de cuenta por cliente (PDF)
- Exportación/Importación de datos (JSON)

## Esquema de Base de Datos

### Tabla: clientes
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | TEXT | UUID del cliente |
| nombre | TEXT | Nombre completo |
| telefono | TEXT | Teléfono de contacto |
| direccion | TEXT | Dirección |
| email | TEXT | Correo electrónico |
| fecha_inicio | TEXT | Fecha de registro |
| total_deuda | REAL | Deuda total |
| total_pagado | REAL | Total pagado |
| saldo_pendiente | REAL | Saldo pendiente |
| estado | TEXT | al_dia/pendiente/atrasado |
| producto | TEXT | Producto/servicio |
| notas | TEXT | Notas adicionales |

### Tabla: pagos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | TEXT | UUID del pago |
| cliente_id | TEXT | Referencia al cliente |
| fecha | TEXT | Fecha del pago |
| monto | REAL | Monto pagado |
| tipo | TEXT | inicial/cuota/abono/liquidacion |
| metodo | TEXT | efectivo/transferencia/deposito/cheque/otro |
| notas | TEXT | Notas del pago |

## Función `registrar_pago`

La función principal que actualiza el saldo del cliente:

```python
def registrar_pago(self, cliente_id: str, monto: float, tipo: str, 
                   metodo: str, notas: str = "") -> str:
    # 1. Obtener cliente actual
    cliente = db.get_cliente_by_id(cliente_id)
    
    # 2. Calcular nuevos valores
    nuevo_total_pagado = cliente['total_pagado'] + monto
    nuevo_saldo = cliente['total_deuda'] - nuevo_total_pagado
    
    # 3. Determinar nuevo estado
    if nuevo_saldo <= 0:
        nuevo_estado = 'al_dia'
    elif nuevo_saldo < cliente['saldo_pendiente']:
        nuevo_estado = 'pendiente'
    else:
        nuevo_estado = 'atrasado'
    
    # 4. Guardar pago y actualizar cliente (transacción)
    # INSERT INTO pagos ...
    # UPDATE clientes SET total_pagado=?, saldo_pendiente=?, estado=? ...
    
    return pago_id
```

## Paleta de Colores (Dark Mode)

| Elemento | Color | Hex |
|----------|-------|-----|
| Background | Slate 900 | `#0f172a` |
| Secondary BG | Slate 800 | `#1e293b` |
| Primary | Teal 500 | `#14b8a6` |
| Text Primary | Slate 50 | `#f8fafc` |
| Text Secondary | Slate 300 | `#cbd5e1` |
| Success | Green 500 | `#22c55e` |
| Warning | Amber 500 | `#f59e0b` |
| Danger | Red 500 | `#ef4444` |

## Dependencias Principales

- `streamlit` - Framework web
- `pandas` - Manipulación de datos
- `plotly` - Gráficos interactivos
- `reportlab` - Generación de PDFs
- `sqlite3` - Base de datos (incluido en Python)

## Personalización

### Cambiar el tema
Edita el archivo `.streamlit/config.toml`:

```toml
[theme]
base = "dark"
primaryColor = "#14b8a6"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#f8fafc"
```

### Cambiar la moneda
Edita `utils.py` y modifica la función `format_currency`:

```python
def format_currency(amount: float, symbol: str = "$") -> str:
    return f"{symbol}{amount:,.2f}"
```

## Despliegue

### Streamlit Cloud (Gratuito)

1. Sube el código a GitHub
2. Conecta tu repositorio en [share.streamlit.io](https://share.streamlit.io)
3. ¡Listo! La app estará disponible en línea

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Capturas de Pantalla

### Dashboard
![Dashboard](https://via.placeholder.com/800x400/0f172a/14b8a6?text=Dashboard)

### Clientes
![Clientes](https://via.placeholder.com/800x400/0f172a/14b8a6?text=Clientes)

### Pagos
![Pagos](https://via.placeholder.com/800x400/0f172a/14b8a6?text=Pagos)

## Licencia

MIT License - Libre para uso personal y comercial.

## Soporte

Para reportar bugs o solicitar funcionalidades, crear un issue en el repositorio.

---

**Desarrollado con** Python, Streamlit y SQLite.
