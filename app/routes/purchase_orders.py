from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required
from app import db
from app.models import PurchaseOrder, PurchaseOrderItem, SparePart
from datetime import datetime

purchase_orders = Blueprint('purchase_orders', __name__)


def generate_po_number():
    last = PurchaseOrder.query.order_by(
        PurchaseOrder.id.desc()
    ).first()
    num = (last.id + 1) if last else 1
    return f"PO-{datetime.now().year}-{num:04d}"


@purchase_orders.route('/purchase-orders')
@login_required
def list_po():
    pos = PurchaseOrder.query.order_by(
        PurchaseOrder.created_at.desc()
    ).all()
    return render_template('purchase_orders/list.html', pos=pos)


@purchase_orders.route('/purchase-orders/create', methods=['GET', 'POST'])
@login_required
def create_po():
    all_parts    = SparePart.query.order_by(SparePart.name).all()
    low_stock    = SparePart.query.filter(
        SparePart.stock <= SparePart.min_stock
    ).all()

    if request.method == 'POST':
        supplier_name    = request.form.get('supplier_name')
        supplier_phone   = request.form.get('supplier_phone')
        supplier_address = request.form.get('supplier_address')
        notes            = request.form.get('notes')

        part_ids    = request.form.getlist('part_id[]')
        part_names  = request.form.getlist('part_name[]')
        quantities  = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')

        if not supplier_name:
            flash('Please enter supplier name!', 'danger')
            return redirect(url_for('purchase_orders.create_po'))

        if not part_ids:
            flash('Please add at least one part to the order!', 'danger')
            return redirect(url_for('purchase_orders.create_po'))

        po = PurchaseOrder(
            po_number        = generate_po_number(),
            supplier_name    = supplier_name,
            supplier_phone   = supplier_phone,
            supplier_address = supplier_address,
            notes            = notes,
            status           = 'pending'
        )
        db.session.add(po)
        db.session.flush()

        total = 0
        for part_id, part_name, qty, price in zip(
            part_ids, part_names, quantities, unit_prices
        ):
            qty   = int(qty)
            price = float(price)
            total_price = qty * price
            total += total_price

            item = PurchaseOrderItem(
                po_id       = po.id,
                part_id     = int(part_id) if part_id else None,
                part_name   = part_name,
                quantity    = qty,
                unit_price  = price,
                total_price = total_price
            )
            db.session.add(item)

        po.total_amount = total
        db.session.commit()
        flash(f'Purchase Order {po.po_number} created successfully!', 'success')
        return redirect(url_for('purchase_orders.po_detail', id=po.id))

    return render_template('purchase_orders/create.html',
                           all_parts=all_parts,
                           low_stock=low_stock)


@purchase_orders.route('/purchase-orders/<int:id>')
@login_required
def po_detail(id):
    from urllib.parse import quote
    po = PurchaseOrder.query.get_or_404(id)

    message = f"""Hello {po.supplier_name},

Purchase Order from Bike Garage

PO Number : {po.po_number}
Date      : {po.created_at.strftime('%d-%m-%Y')}

Items Ordered:
"""
    for item in po.items:
        message += f"- {item.part_name} x{item.quantity} @ Rs {item.unit_price} = Rs {item.total_price}\n"

    message += f"""
Total Amount : Rs {po.total_amount}
Notes        : {po.notes or 'N/A'}

Please confirm and deliver at the earliest.
Thank you,
Bike Garage"""

    whatsapp_message = quote(message)
    return render_template('purchase_orders/detail.html',
                           po=po,
                           whatsapp_message=whatsapp_message)


@purchase_orders.route('/purchase-orders/receive/<int:id>', methods=['POST'])
@login_required
def mark_received(id):
    po = PurchaseOrder.query.get_or_404(id)
    if po.status == 'received':
        flash('This PO is already marked as received!', 'warning')
        return redirect(url_for('purchase_orders.po_detail', id=id))

    for item in po.items:
        if item.part_id:
            part = SparePart.query.get(item.part_id)
            if part:
                part.stock += item.quantity

    po.status = 'received'
    db.session.commit()
    flash(f'PO {po.po_number} marked as received! Stock updated automatically.', 'success')
    return redirect(url_for('purchase_orders.po_detail', id=id))


@purchase_orders.route('/purchase-orders/cancel/<int:id>', methods=['POST'])
@login_required
def cancel_po(id):
    po = PurchaseOrder.query.get_or_404(id)
    po.status = 'cancelled'
    db.session.commit()
    flash(f'PO {po.po_number} cancelled!', 'warning')
    return redirect(url_for('purchase_orders.list_po'))


@purchase_orders.route('/purchase-orders/pdf/<int:id>')
@login_required
def download_po_pdf(id):
    from app.utils.po_pdf import generate_po_pdf
    po     = PurchaseOrder.query.get_or_404(id)
    buffer = generate_po_pdf(po)
    return send_file(
        buffer,
        as_attachment  = True,
        download_name  = f'{po.po_number}.pdf',
        mimetype       = 'application/pdf'
    )