"""
Generador de PDFs - Sistema de Cobranzas (Streamlit)
Genera recibos y reportes en PDF usando ReportLab
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import pandas as pd

# ==================== ESTILOS ====================

def get_styles():
    """Retorna los estilos para los documentos"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CustomTitle',
        fontSize=24,
        textColor=colors.HexColor('#14b8a6'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='CustomSubtitle',
        fontSize=14,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='Label',
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='Value',
        fontSize=12,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    ))
    
    return styles

# ==================== GENERAR RECIBO DE PAGO ====================

def generar_recibo_pago(cliente: dict, pago: dict) -> BytesIO:
    """Genera un recibo de pago en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    styles = get_styles()
    elements = []
    
    # Título
    elements.append(Paragraph("RECIBO DE PAGO", styles['CustomTitle']))
    elements.append(Paragraph("Sistema de Cobranzas", styles['CustomSubtitle']))
    elements.append(Spacer(1, 20))
    
    # Número de recibo
    recibo_num = pago['id'][-8:].upper()
    elements.append(Paragraph(f"<b>Recibo No:</b> {recibo_num}", styles['Value']))
    elements.append(Spacer(1, 20))
    
    # Información del cliente
    elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", styles['SectionTitle']))
    
    cliente_data = [
        ['Nombre:', cliente['nombre']],
        ['Teléfono:', cliente['telefono']],
        ['Dirección:', cliente['direccion']],
        ['Producto:', cliente['producto']],
    ]
    
    if cliente.get('email'):
        cliente_data.append(['Email:', cliente['email']])
    
    cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
    cliente_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 20))
    
    # Detalle del pago
    elements.append(Paragraph("DETALLE DEL PAGO", styles['SectionTitle']))
    
    from utils import format_tipo_pago, format_metodo_pago, format_datetime
    
    pago_data = [
        ['Fecha:', format_datetime(pago['fecha'])],
        ['Tipo:', format_tipo_pago(pago['tipo'])],
        ['Método:', format_metodo_pago(pago['metodo'])],
    ]
    
    if pago.get('notas'):
        pago_data.append(['Notas:', pago['notas']])
    
    pago_table = Table(pago_data, colWidths=[2*inch, 4*inch])
    pago_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(pago_table)
    elements.append(Spacer(1, 30))
    
    # Monto destacado
    monto_box = Table([['MONTO PAGADO', f"${pago['monto']:,.2f}"]], 
                      colWidths=[3*inch, 3*inch])
    monto_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#14b8a6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 12),
        ('FONTSIZE', (1, 0), (1, 0), 24),
        ('PADDING', (0, 0), (-1, -1), 20),
        ('BORDER', (0, 0), (-1, -1), 0),
        ('BORDERRADIUS', (0, 0), (-1, -1), 10),
    ]))
    elements.append(monto_box)
    elements.append(Spacer(1, 30))
    
    # Resumen de cuenta
    elements.append(Paragraph("RESUMEN DE CUENTA", styles['SectionTitle']))
    
    resumen_data = [
        ['Deuda Total:', f"${cliente['total_deuda']:,.2f}"],
        ['Total Pagado:', f"${cliente['total_pagado']:,.2f}"],
        ['Saldo Pendiente:', f"${cliente['saldo_pendiente']:,.2f}"],
    ]
    
    resumen_table = Table(resumen_data, colWidths=[2*inch, 4*inch])
    resumen_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, 1), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#ef4444')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(resumen_table)
    elements.append(Spacer(1, 40))
    
    # Footer
    elements.append(Paragraph(
        f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>"
        "Este recibo es un comprobante oficial de pago.",
        ParagraphStyle('Footer', fontSize=9, textColor=colors.HexColor('#94a3b8'), 
                      alignment=TA_CENTER)
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==================== GENERAR ESTADO DE CUENTA ====================

def generar_estado_cuenta(cliente: dict, pagos: list) -> BytesIO:
    """Genera un estado de cuenta en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    styles = get_styles()
    elements = []
    
    # Título
    elements.append(Paragraph("ESTADO DE CUENTA", styles['CustomTitle']))
    elements.append(Paragraph("Sistema de Cobranzas", styles['CustomSubtitle']))
    elements.append(Spacer(1, 20))
    
    # Información del cliente
    elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", styles['SectionTitle']))
    
    from utils import format_date
    
    cliente_data = [
        ['Nombre:', cliente['nombre']],
        ['Teléfono:', cliente['telefono']],
        ['Dirección:', cliente['direccion']],
        ['Producto:', cliente['producto']],
        ['Fecha de Inicio:', format_date(cliente['fecha_inicio'])],
    ]
    
    cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
    cliente_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 20))
    
    # Resumen financiero
    elements.append(Paragraph("RESUMEN FINANCIERO", styles['SectionTitle']))
    
    resumen_data = [
        ['Deuda Total', 'Total Pagado', 'Saldo Pendiente'],
        [
            f"${cliente['total_deuda']:,.2f}",
            f"${cliente['total_pagado']:,.2f}",
            f"${cliente['saldo_pendiente']:,.2f}"
        ]
    ]
    
    resumen_table = Table(resumen_data, colWidths=[2*inch, 2*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(resumen_table)
    elements.append(Spacer(1, 30))
    
    # Historial de pagos
    if pagos:
        elements.append(Paragraph("HISTORIAL DE PAGOS", styles['SectionTitle']))
        
        from utils import format_tipo_pago, format_metodo_pago, format_date
        
        pagos_data = [['Fecha', 'Tipo', 'Método', 'Monto']]
        
        for pago in pagos:
            pagos_data.append([
                format_date(pago['fecha']),
                format_tipo_pago(pago['tipo']),
                format_metodo_pago(pago['metodo']),
                f"${pago['monto']:,.2f}"
            ])
        
        pagos_table = Table(pagos_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        pagos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        elements.append(pagos_table)
        elements.append(Spacer(1, 20))
        
        # Total de pagos
        elements.append(Paragraph(
            f"<b>Total de pagos registrados: {len(pagos)}</b>",
            ParagraphStyle('Total', fontSize=11, alignment=TA_RIGHT, 
                          textColor=colors.HexColor('#0f172a'))
        ))
    
    # Footer
    elements.append(Spacer(1, 40))
    elements.append(Paragraph(
        f"Estado de cuenta generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>"
        "Sistema de Cobranzas v1.0",
        ParagraphStyle('Footer', fontSize=9, textColor=colors.HexColor('#94a3b8'), 
                      alignment=TA_CENTER)
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==================== GENERAR REPORTE DE CARTERA ====================

def generar_reporte_cartera(resumen: dict, clientes_df: pd.DataFrame) -> BytesIO:
    """Genera un reporte de cartera en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=18)
    
    styles = get_styles()
    elements = []
    
    # Título
    elements.append(Paragraph("REPORTE DE CARTERA", styles['CustomTitle']))
    elements.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y')}", 
                             styles['CustomSubtitle']))
    elements.append(Spacer(1, 20))
    
    # KPIs
    elements.append(Paragraph("RESUMEN GENERAL", styles['SectionTitle']))
    
    kpi_data = [
        ['Total Clientes', 'Al Día', 'Pendientes', 'Atrasados'],
        [
            str(resumen['total_clientes']),
            str(resumen['clientes_al_dia']),
            str(resumen['clientes_pendientes']),
            str(resumen['clientes_atrasados'])
        ]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 20))
    
    # Totales financieros
    fin_data = [
        ['Total Cobrado', 'Por Cobrar'],
        [
            f"${resumen['total_pagado']:,.2f}",
            f"${resumen['total_por_cobrar']:,.2f}"
        ]
    ]
    
    fin_table = Table(fin_data, colWidths=[3*inch, 3*inch])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#22c55e')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(fin_table)
    elements.append(Spacer(1, 30))
    
    # Detalle de clientes
    if not clientes_df.empty:
        elements.append(Paragraph("DETALLE DE CLIENTES", styles['SectionTitle']))
        
        clientes_data = [['Cliente', 'Producto', 'Deuda', 'Pagado', 'Saldo', 'Estado']]
        
        for _, row in clientes_df.iterrows():
            estado_color = {
                'al_dia': '✅',
                'pendiente': '⏳',
                'atrasado': '⚠️'
            }.get(row['estado'], '')
            
            clientes_data.append([
                row['nombre'],
                row['producto'],
                f"${row['total_deuda']:,.2f}",
                f"${row['total_pagado']:,.2f}",
                f"${row['saldo_pendiente']:,.2f}",
                estado_color
            ])
        
        clientes_table = Table(clientes_data, 
                              colWidths=[1.8*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 0.7*inch])
        clientes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        elements.append(clientes_table)
    
    # Footer
    elements.append(Spacer(1, 40))
    elements.append(Paragraph(
        "Sistema de Cobranzas v1.0 - Reporte de Cartera",
        ParagraphStyle('Footer', fontSize=9, textColor=colors.HexColor('#94a3b8'), 
                      alignment=TA_CENTER)
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
