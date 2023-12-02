from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import request, jsonify, redirect, url_for
from models import User, ChargingStation
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/mydatabase'
app.config['SECRET_KEY'] = 'MySecretKey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)


@app.route('register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'}), 201


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
@jwt_required
def register_charging_station():
    data = request.get_jso()
    new_charging_station = ChargingStation(
        name=data['name'],
        location=data['location'],
        charger_types=data['charger_types'],
        availability=data['availability'],
        pricing=data['pricing'],
        opening_hours=data['opening_hours'],
        operator_id=data['operator_id']
    )
    db.session.add(new_charging_station)
    db.session.commit()
    return jsonify({'message': 'Charging station registered successfully'}), 201
