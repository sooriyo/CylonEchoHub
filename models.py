# models.py
from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    charging_stations = db.relationship('ChargingStation', backref='operator', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class ChargingStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    charger_types = db.Column(db.String(255), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    pricing = db.Column(db.String(255), nullable=False)
    opening_hours = db.Column(db.String(255))
    operator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<ChargingStation {self.name}>'
