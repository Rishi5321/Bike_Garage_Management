from flask import send_file
from app.utils.pdf_generator import generate_bill_pdf
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Bill, Service, SparePart, ServicePart

billing = Blueprint('billing', __name__)


@billing.route('/billing')
def list_bills():
    bills = Bill.query.order_by(Bill.created_at.desc()).all()
    return render_template('billing/list.html', bills=bills)


@billing.route('/billing/create/<int:service_id>', methods=['GET', 'POST'])
def create_bill(service_id):
    service = Service.query.get_or_404(service_id)
    parts   = SparePart.query.all()

    if request.method == 'POST':
        part_ids    = request.form.getlist('part_id')
        quantities  = request.form.getlist('quantity')

        parts_total = 0
        for part_id, qty in zip(part_ids, quantities):
            if part_id and int(qty) > 0:
                part          = SparePart.query.get(int(part_id))
                qty           = int(qty)
                price         = part.price * qty
                parts_total  += price

                if part.stock < qty:
                    flash(f'Not enough stock for {part.name}!', 'danger')
                    return redirect(url_for('billing.create_bill', service_id=service_id))

                service_part = ServicePart(
                    service_id = service_id,
                    part_id    = part.id,
                    quantity   = qty,
                    price      = price
                )
                part.stock -= qty
                db.session.add(service_part)

        total_amount = service.cost + parts_total
        bill = Bill(
            service_id   = service_id,
            total_amount = total_amount,
            paid         = False
        )
        db.session.add(bill)
        db.session.commit()
        flash('Bill created successfully!', 'success')
        return redirect(url_for('billing.bill_detail', id=bill.id))

    return render_template('billing/create.html', service=service, parts=parts)


# @billing.route('/billing/<int:id>')
# def bill_detail(id):
#     bill = Bill.query.get_or_404(id)
#     return render_template('billing/detail.html', bill=bill)

@billing.route('/billing/<int:id>')
def bill_detail(id):
    from urllib.parse import quote
    bill = Bill.query.get_or_404(id)

    message = f"""Hello {bill.service.bike.customer.name},

Your bike service at Bike Garage is complete!

Invoice #{bill.id}
Bike     : {bill.service.bike.bike_number} - {bill.service.bike.bike_model}
Service  : {bill.service.service_type}
Amount   : Rs {bill.total_amount}
Status   : {'PAID' if bill.paid else 'UNPAID'}
Date     : {bill.created_at.strftime('%d-%m-%Y')}

Thank you for choosing Bike Garage!
Drive Safe."""

    whatsapp_message = quote(message)
    return render_template('billing/detail.html',
                           bill=bill,
                           whatsapp_message=whatsapp_message)


@billing.route('/billing/pay/<int:id>', methods=['POST'])
def mark_paid(id):
    bill      = Bill.query.get_or_404(id)
    bill.paid = True
    db.session.commit()
    flash('Bill marked as paid!', 'success')
    return redirect(url_for('billing.bill_detail', id=id))

@billing.route('/billing/pdf/<int:id>')
def download_pdf(id):
    bill   = Bill.query.get_or_404(id)
    buffer = generate_bill_pdf(bill)
    return send_file(
        buffer,
        as_attachment      = True,
        download_name      = f'Invoice_BG{bill.id:04d}.pdf',
        mimetype           = 'application/pdf'
    )