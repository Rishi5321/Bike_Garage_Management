from app.ai.chatbot import ask_chatbot
from app.ai.predictor import predict_next_service, get_all_bikes_due
from app.ai.fault_detector import detect_fault
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Service, Bike, Customer
from datetime import datetime

services = Blueprint('services', __name__)

SERVICE_TYPES = [
    'Oil Change',
    'Brake Repair',
    'Engine Check',
    'Chain Adjustment',
    'Tyre Puncture',
    'Battery Replacement',
    'General Service',
    'Clutch Repair',
    'Suspension Repair',
    'Lights & Electrical'
]


@services.route('/services')
def list_services():
    all_services = Service.query.order_by(Service.service_date.desc()).all()
    return render_template('services/list.html', services=all_services)


@services.route('/services/add', methods=['GET', 'POST'])
def add_service():
    bikes = Bike.query.all()
    if request.method == 'POST':
        bike_id      = request.form.get('bike_id')
        service_type = request.form.get('service_type')
        description  = request.form.get('description')
        cost         = request.form.get('cost') or 0.0
        if not bike_id:
            flash('Bike not found Please add a bike !', 'danger')
            return redirect(url_for('services.add_service'))
        service = Service(
            bike_id      = bike_id,
            service_type = service_type,
            description  = description,
            cost         = float(cost),
            status       = 'pending'
        )
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('services.list_services'))

    return render_template('services/add.html', bikes=bikes, service_types=SERVICE_TYPES)


@services.route('/services/<int:id>')
def service_detail(id):
    service = Service.query.get_or_404(id)
    return render_template('services/detail.html', service=service)


@services.route('/services/complete/<int:id>', methods=['POST'])
def complete_service(id):
    service              = Service.query.get_or_404(id)
    service.status       = 'completed'
    service.completed_at = datetime.utcnow()
    db.session.commit()
    flash('Service marked as completed!', 'success')
    return redirect(url_for('services.list_services'))


@services.route('/services/edit/<int:id>', methods=['GET', 'POST'])
def edit_service(id):
    service = Service.query.get_or_404(id)
    bikes   = Bike.query.all()
    if request.method == 'POST':
        service.bike_id      = request.form.get('bike_id')
        service.service_type = request.form.get('service_type')
        service.description  = request.form.get('description')
        service.cost         = float(request.form.get('cost') or 0.0)
        db.session.commit()

        from app.models import Bill, ServicePart
        existing_bill = Bill.query.filter_by(
            service_id=service.id
        ).first()

        if existing_bill:
            parts_total = sum(
                sp.price for sp in service.parts_used
            )
            existing_bill.total_amount = service.cost + parts_total
            db.session.commit()
            flash('Service updated and bill recalculated!', 'success')
        else:
            flash('Service updated!', 'success')

        return redirect(url_for('services.list_services'))

    return render_template('services/edit.html', service=service,
                           bikes=bikes, service_types=SERVICE_TYPES)

@services.route('/services/delete/<int:id>', methods=['POST'])
def delete_service(id):
    service = Service.query.get_or_404(id)

    for part in service.parts_used:
        db.session.delete(part)

    if service.bill:
        for bill in service.bill:
            db.session.delete(bill)

    db.session.delete(service)
    db.session.commit()
    flash('Service deleted!', 'warning')
    return redirect(url_for('services.list_services'))


# @services.route('/services/delete/<int:id>', methods=['POST'])
# def delete_service(id):
#     service = Service.query.get_or_404(id)
#     db.session.delete(service)
#     db.session.commit()
#     flash('Service deleted!', 'warning')
#     return redirect(url_for('services.list_services'))

@services.route('/fault-detection', methods=['GET', 'POST'])
def fault_detection():
    result  = None
    problem = None
    if request.method == 'POST':
        problem = request.form.get('problem')
        result  = detect_fault(problem)
    return render_template('services/fault_detection.html',
                           result=result, problem=problem)

@services.route('/predict/<int:bike_id>')
def predict_service(bike_id):
    from app.models import Bike
    bike   = Bike.query.get_or_404(bike_id)
    result = predict_next_service(bike_id)
    return render_template('services/prediction.html',
                           bike=bike, result=result)


@services.route('/due-services')
def due_services():
    due_bikes = get_all_bikes_due()
    return render_template('services/due_services.html',
                           due_bikes=due_bikes)

@services.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    return render_template('services/chatbot.html')


@services.route('/chatbot/ask', methods=['POST'])
def chatbot_ask():
    from flask import jsonify
    user_message = request.form.get('message')
    if not user_message:
        return jsonify({'reply': 'Please type a message!'})
    result = ask_chatbot(user_message)
    return jsonify({'reply': result['reply']})

@services.route('/send-reminder/<int:bike_id>/<string:service_type>')
# @login_required
def send_reminder(bike_id, service_type):
    from app.models import Bike
    from urllib.parse import quote
    from app.ai.predictor import predict_next_service

    bike   = Bike.query.get_or_404(bike_id)
    result = predict_next_service(bike_id)

    next_due  = ''
    days_left = ''

    if result['has_prediction']:
        for p in result['predictions']:
            if p['service_type'] == service_type:
                next_due  = p['next_due']
                days_left = p['days_left']
                break

    message = f"""Hello {bike.customer.name},

This is a reminder from Bike Garage.

Your bike {bike.bike_number} ({bike.bike_model}) is due for:
Service  : {service_type}
Due Date : {next_due}
Days Left: {days_left} days

Please visit us soon for timely service!

Thank you,
Bike Garage 🔧"""

    whatsapp_url = f"https://wa.me/91{bike.customer.phone}?text={quote(message)}"
    return redirect(whatsapp_url)