# app.py
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://@localhost:5432/CylonEchoPlug'
app.config['SECRET_KEY'] = 'MySecretKey'

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Import models
from models import User, ChargingStation


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({'message': 'Logged in successfully!', 'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401


@app.route('/charging_stations', methods=['POST'])
@jwt_required()
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


@app.route('/charging_stations', methods=['GET'])
def charging_stations():
    stations = ChargingStation.query.all()
    station_list = [{'name': station.name, 'location': station.location} for station in stations]
    return jsonify(station_list), 200


@app.errorhandler(404)
def not_found(_):
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
