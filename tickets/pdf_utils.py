from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from io import BytesIO
import datetime

def generar_pdf_ticket_anonimo(ticket):
    """
    Genera un PDF con la información del ticket anónimo
    """
    # Crear el buffer en memoria
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#111827'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para subtítulos
    subtitulo_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#111827'),
        spaceBefore=20,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Estilo para información destacada
    destacado_style = ParagraphStyle(
        'CustomDestacado',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#059669'),
        spaceBefore=10,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    # Contenido del PDF
    story = []
    
    # Encabezado
    story.append(Paragraph("TALENTO ESCUCHA", titulo_style))
    story.append(Paragraph("Comprobante de Solicitud Anónima", subtitulo_style))
    story.append(Spacer(1, 20))
    
    # Información del ticket destacada
    story.append(Paragraph(f"Código de Ticket: <b>{ticket.codigo}</b>", destacado_style))
    story.append(Spacer(1, 20))
    
    # Fecha de creación
    fecha_creacion = ticket.fecha_creacion.strftime("%d/%m/%Y %H:%M:%S")
    story.append(Paragraph(f"<b>Fecha de Creación:</b> {fecha_creacion}", normal_style))
    story.append(Spacer(1, 15))
    
    # Información de la solicitud en tabla
    data = [
        ['Campo', 'Información'],
        ['Código del Ticket', ticket.codigo],
        ['Agencia', ticket.agencia.nombre if ticket.agencia else 'N/A'],
        ['Tipo de Solicitud', ticket.get_tipo_solicitud_display()],
        ['Severidad', ticket.get_severidad_display()],
        ['Estado', ticket.get_estado_display()],
        ['Fecha de Creación', fecha_creacion],
    ]
    
    # Crear tabla
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Descripción
    if ticket.descripcion:
        story.append(Paragraph("Descripción de la Solicitud:", subtitulo_style))
        story.append(Paragraph(ticket.descripcion, normal_style))
        story.append(Spacer(1, 20))
    
    # Instrucciones importantes
    story.append(Paragraph("Instrucciones Importantes:", subtitulo_style))
    instrucciones = [
        "• Guarde este comprobante para futuras consultas sobre su solicitud.",
        "• Su código de ticket es único y necesario para dar seguimiento.",
        "• El tiempo de respuesta puede variar según la complejidad de la solicitud.",
        "• Para consultas adicionales, presente este código en nuestras oficinas."
    ]
    
    for instruccion in instrucciones:
        story.append(Paragraph(instruccion, normal_style))
    
    story.append(Spacer(1, 30))
    
    # Pie de página
    story.append(Paragraph("Gracias por confiar en nuestros servicios", 
                         ParagraphStyle('Footer', 
                                      parent=styles['Normal'],
                                      fontSize=10,
                                      textColor=colors.HexColor('#6b7280'),
                                      alignment=TA_CENTER)))
    
    # Construir el PDF
    doc.build(story)
    
    # Obtener el contenido del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf