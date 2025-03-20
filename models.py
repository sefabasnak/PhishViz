# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    scenario = db.Column(db.String(200))
    domain = db.Column(db.String(100))
    logo = db.Column(db.String(200))
    tests = db.relationship('Test', backref='customer', lazy=True)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    data_leaks = db.Column(db.Integer, default=0)
    mail_sent = db.Column(db.Integer, default=0)
    mail_read = db.Column(db.Integer, default=0)
    link_clicked = db.Column(db.Integer, default=0)
    exec_count = db.Column(db.Integer, default=0)
    reports = db.relationship('Report', backref='test', lazy=True)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    ip_address = db.Column(db.String(15))
    location = db.Column(db.String(100))
    coords_lat = db.Column(db.Float, default=0.0)
    coords_lon = db.Column(db.Float, default=0.0)
    data_leak = db.Column(db.Boolean, default=False)