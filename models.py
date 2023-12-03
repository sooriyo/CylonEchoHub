from flask_login import UserMixin
from datetime import datetime
from extensions import db


# Define User model for database
class User(UserMixin, db.Model):
    # Define columns for the User table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Define relationship to ChargingStation model
    charging_stations = db.relationship('ChargingStation', backref='operator', lazy=True)
    # New fields for email verification
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(6), nullable=True)

    def __init__(self, username, email, password, email_verification_token):
        self.username = username
        self.email = email
        self.password = password
        self.email_verification_token = email_verification_token


# Define ChargingStation model for database
class ChargingStation(db.Model):
    # Define columns for the ChargingStation table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    charger_types = db.Column(db.String(255), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    pricing = db.Column(db.String(255), nullable=False)
    opening_hours = db.Column(db.String(255))
    # Foreign key reference to User model
    operator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<ChargingStation {self.name}>'
