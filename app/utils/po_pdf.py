from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io


def generate_po_pdf(po):
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=20*mm, leftMargin=20*mm,
                               topMargin=20*mm, bottomMargin=20*mm)
    styles   = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'title', parent=styles['Normal'],
        fontSize=22, fontName='Helvetica-Bold',
        alignment=TA_CENTER, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'subtitle', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica',
        alignment=TA_CENTER, spaceAfter=2,
        textColor=colors.grey
    )
    heading_style = ParagraphStyle(
        'heading', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold',
        spaceAfter=6, spaceBefore=10
    )
    normal_style = ParagraphStyle(
        'normal', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica', spaceAfter=3
    )

    # Header
    elements.append(Paragraph("Bike Garage", title_style))
    elements.append(Paragraph("Professional Bike Repair & Service", subtitle_style))
    elements.append(Paragraph("Pune, Maharashtra | Phone: 9999999999", subtitle_style))
    elements.append(Spacer(1, 4*mm))

    divider = Table([['']], colWidths=[170*mm])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 2, colors.HexColor('#2E4057')),
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 4*mm))

    # PO Info
    elements.append(Paragraph("PURCHASE ORDER", ParagraphStyle(
        'po', parent=styles['Normal'],
        fontSize=16, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2E4057'), spaceAfter=8
    )))

    status_color = {
        'pending'   : '#F4A435',
        'received'  : '#4CAF82',
        'cancelled' : '#E05555'
    }.get(po.status, '#888888')

    po_info = [
        ['PO Number',  ':', po.po_number],
        ['Date',       ':', po.created_at.strftime('%d-%m-%Y')],
        
    ]

    po_table = Table(po_info, colWidths=[35*mm, 5*mm, 130*mm])
    po_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 11),
        ('TEXTCOLOR', (2,2), (2,2), colors.HexColor(status_color)),
        ('FONTNAME',  (2,2), (2,2), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
    ]))
    elements.append(po_table)
    elements.append(Spacer(1, 5*mm))

    # Supplier Details
    elements.append(divider)
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("Supplier Details", heading_style))

    sup_info = [
        ['Supplier Name', ':', po.supplier_name],
        ['Phone',         ':', po.supplier_phone   or 'N/A'],
        ['Address',       ':', po.supplier_address or 'N/A'],
    ]
    sup_table = Table(sup_info, colWidths=[35*mm, 5*mm, 130*mm])
    sup_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 11),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
    ]))
    elements.append(sup_table)
    elements.append(Spacer(1, 5*mm))

    # Items Table
    elements.append(divider)
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("Order Items", heading_style))

    item_data = [['#', 'Part Name', 'Qty', 'Unit Price', 'Total']]
    for i, item in enumerate(po.items, 1):
        item_data.append([
            str(i),
            item.part_name,
            str(item.quantity),
            
        ])

    item_data.append(['', '', ''])
    item_data.append(['', 'Total Parts', str(len(po.items)) + ' items'])
    item_table = Table(item_data, colWidths=[10*mm, 120*mm, 40*mm])
    item_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 11),
        ('ALIGN',         (2,0), (-1,-1), 'RIGHT'),
        ('FONTNAME',      (0,1), (-1,-2), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-2), 10),
        ('ROWBACKGROUNDS',(0,1), (-1,-3),
         [colors.white, colors.HexColor('#F5F5F5')]),
        ('BACKGROUND',    (0,-1), (-1,-1), colors.HexColor('#EEF2F7')),
        ('FONTNAME',      (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,-1), (-1,-1), 12),
        ('LINEABOVE',     (0,-1), (-1,-1), 1.5, colors.HexColor('#2E4057')),
        ('GRID',          (0,0),  (-1,-3), 0.5, colors.HexColor('#CCCCCC')),
        ('BOTTOMPADDING', (0,0),  (-1,-1), 8),
        ('TOPPADDING',    (0,0),  (-1,-1), 8),
        ('LEFTPADDING',   (0,0),  (-1,-1), 8),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 5*mm))

    # Notes
    if po.notes:
        elements.append(Paragraph("Notes", heading_style))
        elements.append(Paragraph(po.notes, normal_style))
        elements.append(Spacer(1, 5*mm))

    # Signature
    elements.append(divider)
    elements.append(Spacer(1, 8*mm))
    sig_data = [
        ['Authorized Signature', '', 'Supplier Acknowledgement'],
        ['', '', ''],
        ['____________________', '', '____________________'],
        ['Garage Owner', '', 'Supplier'],
    ]
    sig_table = Table(sig_data, colWidths=[60*mm, 50*mm, 60*mm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('ALIGN',     (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME',  (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,0), 'Helvetica-Bold'),
        ('TOPPADDING',(0,0), (-1,-1), 6),
    ]))
    elements.append(sig_table)

    elements.append(Spacer(1, 6*mm))
    elements.append(divider)
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        "Thank you for your business partnership — Bike Garage",
        ParagraphStyle('footer', parent=styles['Normal'],
                       fontSize=10, alignment=TA_CENTER,
                       textColor=colors.grey)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer