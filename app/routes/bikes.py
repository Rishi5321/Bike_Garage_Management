from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Bike, Customer

bikes = Blueprint('bikes', __name__)


@bikes.route('/bikes')
def list_bikes():
    all_bikes = Bike.query.order_by(Bike.created_at.desc()).all()
    return render_template('bikes/list.html', bikes=all_bikes)

@bikes.route('/bikes/add', methods=['GET', 'POST'])
def add_bike():
    customers = Customer.query.all()
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        bike_number = request.form.get('bike_number')
        bike_model  = request.form.get('bike_model')
        brand       = request.form.get('brand')
        year        = request.form.get('year') or None

        if not customer_id:
            flash('Please add a customer first!', 'danger')
            return redirect(url_for('bikes.add_bike'))

        existing = Bike.query.filter_by(bike_number=bike_number).first()
        if existing:
            flash('Bike with this number already exists!', 'danger')
            return redirect(url_for('bikes.add_bike'))

        bike = Bike(
            customer_id = customer_id,
            bike_number = bike_number,
            bike_model  = bike_model,
            brand       = brand,
            year        = year
        )
        db.session.add(bike)
        db.session.commit()
        flash('Bike registered successfully!', 'success')
        return redirect(url_for('bikes.list_bikes'))

    return render_template('bikes/add.html', customers=customers)


# @bikes.route('/bikes/add', methods=['GET', 'POST'])
# def add_bike():
#     customers = Customer.query.all()
#     if request.method == 'POST':
#         customer_id = request.form.get('customer_id')
#         bike_number = request.form.get('bike_number')
#         bike_model  = request.form.get('bike_model')
#         brand       = request.form.get('brand')
#         year        = request.form.get('year') or None

#         existing = Bike.query.filter_by(bike_number=bike_number).first()
#         if existing:
#             flash('Bike with this number already exists!', 'danger')
#             return redirect(url_for('bikes.add_bike'))

#         bike = Bike(
#             customer_id=customer_id,
#             bike_number=bike_number,
#             bike_model=bike_model,
#             brand=brand,
#             year=year
#         )
#         db.session.add(bike)
#         db.session.commit()
#         flash('Bike registered successfully!', 'success')
#         return redirect(url_for('bikes.list_bikes'))

#     return render_template('bikes/add.html', customers=customers)


@bikes.route('/bikes/<int:id>')
def bike_detail(id):
    bike = Bike.query.get_or_404(id)
    return render_template('bikes/detail.html', bike=bike)


@bikes.route('/bikes/edit/<int:id>', methods=['GET', 'POST'])
def edit_bike(id):
    bike      = Bike.query.get_or_404(id)
    customers = Customer.query.all()
    if request.method == 'POST':
        bike.customer_id = request.form.get('customer_id')
        bike.bike_number = request.form.get('bike_number')
        bike.bike_model  = request.form.get('bike_model')
        bike.brand       = request.form.get('brand')
        bike.year        = request.form.get('year') 
        db.session.commit()
        flash('Bike updated successfully!', 'success')
        return redirect(url_for('bikes.list_bikes'))
    return render_template('bikes/edit.html', bike=bike, customers=customers)

@bikes.route('/bikes/delete/<int:id>', methods=['POST'])
def delete_bike(id):
    bike = Bike.query.get_or_404(id)

    for service in bike.services:
        for part in service.parts_used:
            db.session.delete(part)
        if service.bill:
            for bill in service.bill:
                db.session.delete(bill)
        db.session.delete(service)

    db.session.delete(bike)
    db.session.commit()
    flash('Bike and all related records deleted!', 'warning')
    return redirect(url_for('bikes.list_bikes'))


# @bikes.route('/bikes/delete/<int:id>', methods=['POST'])
# def delete_bike(id):
#     bike = Bike.query.get_or_404(id)
#     db.session.delete(bike)
#     db.session.commit()
#     flash('Bike deleted!', 'warning')
#     return redirect(url_for('bikes.list_bikes'))