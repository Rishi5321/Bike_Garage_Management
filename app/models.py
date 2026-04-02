from app import db
from flask_login import UserMixin
from datetime import datetime
from app import login
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    role       = db.Column(db.String(20), default='owner')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# class User(UserMixin, db.Model):
#     __tablename__ = 'users'
#     id            = db.Column(db.Integer, primary_key=True)
#     username      = db.Column(db.String(80), unique=True, nullable=False)
#     email         = db.Column(db.String(120), unique=True, nullable=False)
#     password      = db.Column(db.String(200), nullable=False)
#     role          = db.Column(db.String(20), default='mechanic')
#     created_at    = db.Column(db.DateTime, default=datetime.utcnow)


class Customer(db.Model):
    __tablename__ = 'customers'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    phone         = db.Column(db.String(15), unique=True, nullable=False)
    email         = db.Column(db.String(120))
    address       = db.Column(db.String(200))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    bikes         = db.relationship('Bike', backref='customer', lazy=True)


class Bike(db.Model):
    __tablename__ = 'bikes'
    id            = db.Column(db.Integer, primary_key=True)
    customer_id   = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    bike_number   = db.Column(db.String(20), unique=True, nullable=False)
    bike_model    = db.Column(db.String(100), nullable=False)
    brand         = db.Column(db.String(100))
    year          = db.Column(db.Integer)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    services      = db.relationship('Service', backref='bike', lazy=True)


class Service(db.Model):
    __tablename__ = 'services'
    id            = db.Column(db.Integer, primary_key=True)
    bike_id       = db.Column(db.Integer, db.ForeignKey('bikes.id'), nullable=False)
    service_type  = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text)
    status        = db.Column(db.String(20), default='pending')
    service_date  = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at  = db.Column(db.DateTime)
    cost          = db.Column(db.Float, default=0.0)
    parts_used    = db.relationship('ServicePart', backref='service', lazy=True)
    bill          = db.relationship('Bill', backref='service', lazy=True)


class SparePart(db.Model):
    __tablename__ = 'spare_parts'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    category      = db.Column(db.String(50))
    price         = db.Column(db.Float, nullable=False)
    stock         = db.Column(db.Integer, default=0)
    min_stock     = db.Column(db.Integer, default=5)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)


class ServicePart(db.Model):
    __tablename__ = 'service_parts'
    id            = db.Column(db.Integer, primary_key=True)
    service_id    = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    part_id       = db.Column(db.Integer, db.ForeignKey('spare_parts.id'), nullable=False)
    quantity      = db.Column(db.Integer, default=1)
    price         = db.Column(db.Float, nullable=False)
    part          = db.relationship('SparePart')


class Bill(db.Model):
    __tablename__ = 'bills'
    id            = db.Column(db.Integer, primary_key=True)
    service_id    = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    total_amount  = db.Column(db.Float, nullable=False)
    paid          = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'
    id          = db.Column(db.Integer, primary_key=True)
    part_id     = db.Column(db.Integer, db.ForeignKey('spare_parts.id'), nullable=True)
    part_name   = db.Column(db.String(100), nullable=False)
    action      = db.Column(db.String(50), nullable=False)
    quantity    = db.Column(db.Integer, nullable=True)
    old_value   = db.Column(db.Float, nullable=True)
    new_value   = db.Column(db.Float, nullable=True)
    command     = db.Column(db.String(300), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    part        = db.relationship('SparePart', backref='logs')

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))