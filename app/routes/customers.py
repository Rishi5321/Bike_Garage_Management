from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Customer

customers = Blueprint('customers', __name__)


@customers.route('/customers')
def list_customers():
    all_customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('customers/list.html', customers=all_customers)


@customers.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name    = request.form.get('name')
        phone   = request.form.get('phone')
        email   = request.form.get('email')
        address = request.form.get('address')

        existing = Customer.query.filter_by(phone=phone).first()
        if existing:
            flash('Customer with this phone number already exists!', 'danger')
            return redirect(url_for('customers.add_customer'))

        customer = Customer(name=name, phone=phone, email=email, address=address)
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers.list_customers'))

    return render_template('customers/add.html')


@customers.route('/customers/<int:id>')
def customer_detail(id):
    customer = Customer.query.get_or_404(id)
    return render_template('customers/detail.html', customer=customer)


@customers.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name    = request.form.get('name')
        customer.phone   = request.form.get('phone')
        customer.email   = request.form.get('email')
        customer.address = request.form.get('address')
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customers.list_customers'))
    return render_template('customers/edit.html', customer=customer)


# @customers.route('/customers/delete/<int:id>', methods=['POST'])
# def delete_customer(id):
#     customer = Customer.query.get_or_404(id)
#     db.session.delete(customer)
#     db.session.commit()
#     flash('Customer deleted!', 'warning')
#     return redirect(url_for('customers.list_customers'))

@customers.route('/customers/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    
    for bike in customer.bikes:
        for service in bike.services:
            for part in service.parts_used:
                db.session.delete(part)
            if service.bill:
                for bill in service.bill:
                    db.session.delete(bill)
            db.session.delete(service)
        db.session.delete(bike)
    
    db.session.delete(customer)
    db.session.commit()
    flash('Customer and all related records deleted!', 'warning')
    return redirect(url_for('customers.list_customers'))