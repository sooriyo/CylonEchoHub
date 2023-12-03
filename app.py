from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask import Flask, render_template, request, jsonify
from flask_login import login_user, login_required, logout_user
from flask_mail import Mail
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from extensions import db, mail
from flask_login import LoginManager

import email_utils

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://@localhost:5432/CylonEchoPlug'
app.config['SECRET_KEY'] = 'MySecretKey'
db.init_app(app)
mail.init_app(app)

# Initialize extensions
bcrypt = Bcrypt(app)  # Bcrypt for password hashing
jwt = JWTManager(app)  # JWT Manager for token based authentication
migrate = Migrate(app, db)  # Flask-Migrate for database migration
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'tharukaravisara@gmail.com'
app.config['MAIL_PASSWORD'] = 'mcdczvauwnkkipur'
app.config['MAIL_DEFAULT_SENDER'] = 'tharukaravisara@gmail.com'
mail = Mail(app)

# Import models
from models import User, ChargingStation


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Define the home route
@app.route('/')
def home():
    return render_template('home.html')  # Render the home page


# User registration
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()  # Get data from request body
        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        # Create a new user instance

        email_verification_token = email_utils.generate_verification_token()  # Generate verification token
        new_user = User(username=data['username'],
                        email=data['email'],
                        password=hashed_password,
                        email_verification_token=email_verification_token)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Send email verification
        email_utils.send_verification_email(new_user)

        return jsonify({'message': 'Please check your email to verify. '}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/verify_email', methods=['POST'])
def verify_email():
    # Extract verification code from request
    user_id = request.json.get('user_id')
    verification_code = request.json.get('verification_code')

    # Find user by id and verification code
    user = User.query.get(user_id)
    if user and user.email_verification_code == verification_code:
        user.email_verified = True
        user.email_verification_code = None  # Clear verification code
        db.session.commit()
        return jsonify({'message': 'Email verified successfully'}), 200
    else:
        return jsonify({'error': 'Invalid verification code'}), 400


# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()  # Find user by email

    # Check if user exists verified and password is correct
    if user and bcrypt.check_password_hash(user.password, data['password']):
        if user.email_verified:
            login_user(user)  # Handles user session
            return jsonify({'message': 'Logged in successfully!'}), 200
        else:
            return jsonify({'error': 'Please verify your email.'}), 400
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401


# Register a charging station
@app.route('/charging_stations', methods=['POST'])
@jwt_required()  # Require JWT token for authentication
def register_charging_station():
    data = request.get_json()
    new_charging_station = ChargingStation(
        name=data['name'],
        location=data['location'],
        charger_types=data['charger_types'],
        availability=data['availability'],
        pricing=data['pricing'],
        opening_hours=data['opening_hours'],
        operator_id=get_jwt_identity()
    )
    db.session.add(new_charging_station)
    db.session.commit()
    return jsonify({'message': 'Charging station registered successfully'}), 201


# Get user profile
@app.route('/user_profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'charging_stations': [{'name': station.name, 'location': station.location} for station in
                              user.charging_stations]
    }
    return jsonify({'user': user_data}), 200


# Get all charging stations
@app.route('/charging_stations', methods=['GET'])
def charging_stations():
    stations = ChargingStation.query.all()
    station_list = [{'name': station.name, 'location': station.location} for station in stations]
    return jsonify(station_list), 200


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully!'}), 200


# Error 404 Not Found
@app.errorhandler(404)
def not_found(_):
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
