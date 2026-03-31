import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), 
                          '../../ml_models/service_predictor.pkl')

SERVICE_INTERVALS = {
    'Oil Change'           : 90,
    'General Service'      : 1,
    'Brake Repair'         : 120,
    'Chain Adjustment'     : 60,
    'Engine Check'         : 180,
    'Battery Replacement'  : 365,
    'Tyre Puncture'        : None,
    'Clutch Repair'        : 180,
    'Suspension Repair'    : 365,
    'Lights & Electrical'  : 180
}


def predict_next_service(bike_id):
    from app.models import Service

    services = Service.query.filter_by(
        bike_id=bike_id,
        status='completed'
    ).order_by(Service.completed_at.desc()).all()

    if not services:
        return {
            "has_prediction" : False,
            "message"        : "No service history found for this bike."
        }

    predictions = []

    service_types_done = {}
    for s in services:
        if s.service_type not in service_types_done:
            service_types_done[s.service_type] = s.completed_at

    for service_type, last_date in service_types_done.items():
        interval = SERVICE_INTERVALS.get(service_type)
        if interval is None:
            continue

        next_date = last_date + timedelta(days=interval)
        days_left = (next_date - datetime.utcnow()).days

        if days_left <= 30:
            status = "due_soon"
        elif days_left <= 0:
            status = "overdue"
        else:
            status = "ok"

        predictions.append({
            "service_type" : service_type,
            "last_done"    : last_date.strftime('%d-%m-%Y'),
            "next_due"     : next_date.strftime('%d-%m-%Y'),
            "days_left"    : days_left,
            "status"       : status
        })

    predictions.sort(key=lambda x: x['days_left'])

    return {
        "has_prediction" : True,
        "predictions"    : predictions
    }


def get_all_bikes_due():
    from app.models import Bike
    bikes     = Bike.query.all()
    due_bikes = []

    for bike in bikes:
        result = predict_next_service(bike.id)
        if result['has_prediction']:
            for p in result['predictions']:
                if p['status'] in ['due_soon', 'overdue']:
                    due_bikes.append({
                        "bike_id"      : bike.id,
                        "bike_number"  : bike.bike_number,
                        "bike_model"   : bike.bike_model,
                        "customer"     : bike.customer.name,
                        "phone"        : bike.customer.phone,
                        "service_type" : p['service_type'],
                        "next_due"     : p['next_due'],
                        "days_left"    : p['days_left'],
                        "status"       : p['status']
                    })

    return due_bikes

# def get_all_bikes_due():
#     from app.models import Bike
#     bikes     = Bike.query.all()
#     due_bikes = []

#     for bike in bikes:
#         result = predict_next_service(bike.id)
#         if result['has_prediction']:
#             for p in result['predictions']:
#                 if p['status'] in ['due_soon', 'overdue']:
#                     due_bikes.append({
#                         "bike_number"  : bike.bike_number,
#                         "bike_model"   : bike.bike_model,
#                         "customer"     : bike.customer.name,
#                         "phone"        : bike.customer.phone,
#                         "service_type" : p['service_type'],
#                         "next_due"     : p['next_due'],
#                         "days_left"    : p['days_left'],
#                         "status"       : p['status']
#                     })

#     return due_bikes