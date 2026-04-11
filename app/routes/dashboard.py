from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Customer, Bike, Service, Bill, SparePart
from datetime import date

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('home.html')


@dashboard.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    today = date.today()

    total_customers  = Customer.query.count()
    total_bikes      = Bike.query.count()
    pending_services = Service.query.filter_by(status='pending').count()
    low_stock_parts  = SparePart.query.filter(
                           SparePart.stock <= SparePart.min_stock).all()

    # today_bills    = Bill.query.filter(
    #                      db.func.date(Bill.created_at) == today).all()
    # today_revenue  = sum(b.total_amount for b in today_bills if b.paid)
    all_paid_bills  = Bill.query.filter_by(paid=True).all()
    today_revenue   = sum(b.total_amount for b in all_paid_bills
                      if b.created_at.date() == today)
    total_revenue   = sum(b.total_amount for b in all_paid_bills)
    today_serviced = Service.query.filter(
                         db.func.date(Service.completed_at) == today).count()

    recent_services = Service.query.order_by(
                          Service.service_date.desc()).limit(5).all()
    recent_bills    = Bill.query.order_by(
                          Bill.created_at.desc()).limit(5).all()

    return render_template('dashboard.html',
        total_customers  = total_customers,
        total_bikes      = total_bikes,
        pending_services = pending_services,
        low_stock_parts  = low_stock_parts,
        today_revenue    = today_revenue,
        total_revenue    = total_revenue,
        today_serviced   = today_serviced,
        recent_services  = recent_services,
        recent_bills     = recent_bills,
        today            = today
    )


@dashboard.route('/revenue-history')
@login_required
def revenue_history():
    from sqlalchemy import func
    
    daily_revenue = db.session.query(
        func.date(Bill.created_at).label('date'),
        func.count(Bill.id).label('total_bills'),
        func.sum(Bill.total_amount).label('total_revenue')
    ).filter(
        Bill.paid == True
    ).group_by(
        func.date(Bill.created_at)
    ).order_by(
        func.date(Bill.created_at).desc()
    ).all()

    return render_template('dashboard/revenue_history.html',
                           daily_revenue=daily_revenue)



@dashboard.route('/monthly-revenue')
@login_required
def monthly_revenue():
    from sqlalchemy import func

    monthly = db.session.query(
        func.year(Bill.created_at).label('year'),
        func.month(Bill.created_at).label('month'),
        func.count(Bill.id).label('total_bills'),
        func.sum(Bill.total_amount).label('total_revenue')
    ).filter(
        Bill.paid == True
    ).group_by(
        func.year(Bill.created_at),
        func.month(Bill.created_at)
    ).order_by(
        func.year(Bill.created_at).desc(),
        func.month(Bill.created_at).desc()
    ).all()

    month_names = {
        1:'January', 2:'February', 3:'March',
        4:'April',   5:'May',      6:'June',
        7:'July',    8:'August',   9:'September',
        10:'October',11:'November',12:'December'
    }

    return render_template('dashboard/monthly_revenue.html',
                           monthly=monthly,
                           month_names=month_names)



@dashboard.route('/revenue-history-data')
@login_required
def revenue_history_data():
    from flask import jsonify
    from sqlalchemy import func

    daily = db.session.query(
        func.date(Bill.created_at).label('date'),
        func.sum(Bill.total_amount).label('total')
    ).filter(Bill.paid == True).group_by(
        func.date(Bill.created_at)
    ).order_by(func.date(Bill.created_at).desc()).limit(7).all()

    daily   = list(reversed(daily))
    labels  = [str(d.date) for d in daily]
    values  = [float(d.total) for d in daily]

    return jsonify({ 'labels': labels, 'values': values })
# from flask import Blueprint, render_template

# @dashboard.route('/')
# def index():
#     today = date.today()

#     total_customers  = Customer.query.count()
#     total_bikes      = Bike.query.count()
#     pending_services = Service.query.filter_by(status='pending').count()
#     low_stock_parts  = SparePart.query.filter(
#                            SparePart.stock <= SparePart.min_stock).all()

#     today_bills    = Bill.query.filter(
#                          db.func.date(Bill.created_at) == today).all()
#     today_revenue  = sum(b.total_amount for b in today_bills if b.paid)
#     today_serviced = Service.query.filter(
#                          db.func.date(Service.completed_at) == today).count()

#     recent_services = Service.query.order_by(
#                           Service.service_date.desc()).limit(5).all()
#     recent_bills    = Bill.query.order_by(
#                           Bill.created_at.desc()).limit(5).all()

#     return render_template('dashboard.html',
#         total_customers  = total_customers,
#         total_bikes      = total_bikes,
#         pending_services = pending_services,
#         low_stock_parts  = low_stock_parts,
#         today_revenue    = today_revenue,
#         today_serviced   = today_serviced,
#         recent_services  = recent_services,
#         recent_bills     = recent_bills,
#         today            = today
#     )