from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io


def generate_bill_pdf(bill):
    buffer   = io.BytesIO()
    doc      = SimpleDocTemplate(buffer, pagesize=A4,
                                  rightMargin=20*mm, leftMargin=20*mm,
                                  topMargin=20*mm, bottomMargin=20*mm)
    styles   = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'title', parent=styles['Normal'],
        fontSize=20, fontName='Helvetica-Bold',
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
        spaceAfter=6, spaceBefore=12
    )
    normal_style = ParagraphStyle(
        'normal', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica', spaceAfter=4
    )

    elements.append(Paragraph("Bike Garage", title_style))
    elements.append(Paragraph("Professional Bike Repair & Service", subtitle_style))
    elements.append(Paragraph("Pune, Maharashtra | Phone: 9999999999", subtitle_style))
    elements.append(Spacer(1, 6*mm))

    divider = Table([['']], colWidths=[170*mm])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1.5, colors.HexColor('#2E4057')),
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 4*mm))

    elements.append(Paragraph(f"Invoice #BG{bill.id:04d}", heading_style))

    info_data = [
        ['Customer Name', ':', bill.service.bike.customer.name],
        ['Phone',         ':', bill.service.bike.customer.phone],
        ['Bike Number',   ':', bill.service.bike.bike_number],
        ['Bike Model',    ':', bill.service.bike.bike_model],
        ['Invoice Date',  ':', bill.created_at.strftime('%d-%m-%Y')],
        ['Status',        ':', 'PAID' if bill.paid else 'UNPAID'],
    ]

    info_table = Table(info_data, colWidths=[45*mm, 5*mm, 110*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (2,5), (2,5),
         colors.HexColor('#28a745') if bill.paid else colors.HexColor('#dc3545')),
        ('FONTNAME',  (2,5), (2,5), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6*mm))

    elements.append(divider)
    elements.append(Spacer(1, 4*mm))

    elements.append(Paragraph("Service Charges", heading_style))
    bill_data = [['Service Type', 'Amount (Rs)']]
    bill_data.append([
        bill.service.service_type,
        f"Rs {bill.service.cost:.2f}"
    ])

    bill_table = Table(bill_data, colWidths=[130*mm, 40*mm])
    bill_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 11),
        ('ALIGN',         (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1), 10),
        ('ROWBACKGROUNDS',(0,1), (-1,-1),
         [colors.white, colors.HexColor('#F5F5F5')]),
        ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ]))
    elements.append(bill_table)
    elements.append(Spacer(1, 4*mm))

    if bill.service.parts_used:
        elements.append(Paragraph("Parts Used", heading_style))
        parts_data = [['Part Name', 'Amount (Rs)']]
        for sp in bill.service.parts_used:
            parts_data.append([
                f"{sp.part.name} x{sp.quantity}",
                f"Rs {sp.price:.2f}"
            ])

        parts_table = Table(parts_data, colWidths=[130*mm, 40*mm])
        parts_table.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#534AB7')),
            ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
            ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,0), 11),
            ('ALIGN',         (1,0), (1,-1), 'RIGHT'),
            ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',      (0,1), (-1,-1), 10),
            ('ROWBACKGROUNDS',(0,1), (-1,-1),
             [colors.white, colors.HexColor('#F5F5F5')]),
            ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING',    (0,0), (-1,-1), 8),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ]))
        elements.append(parts_table)
        elements.append(Spacer(1, 4*mm))

    total_data = [['TOTAL AMOUNT', f"Rs {bill.total_amount:.2f}"]]
    total_table = Table(total_data, colWidths=[130*mm, 40*mm])
    total_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 12),
        ('ALIGN',         (1,0), (1,0),  'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING',    (0,0), (-1,0), 10),
        ('LEFTPADDING',   (0,0), (-1,0), 8),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 8*mm))

    elements.append(divider)
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph(
        "Thank you for choosing Bike Garage! Drive safe.",
        ParagraphStyle('footer', parent=styles['Normal'],
                       fontSize=10, alignment=TA_CENTER,
                       textColor=colors.grey)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer