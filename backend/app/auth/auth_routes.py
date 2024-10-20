import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from backend.app import db
from backend.app.auth.models import User

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or 'username' not in data or 'email' not in data or 'password' not in data or 'phone_number' not in data:
        return jsonify({'message': 'Missing username, email, password, or phone number'}), 400

    if not EMAIL_REGEX.match(data['email']):
        return jsonify({'message': 'Invalid email format'}), 400

    if not PASSWORD_REGEX.match(data['password']):
        return jsonify({'message': 'Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character.'}), 400

    hashed_password = generate_password_hash(data['password'], method='sha256')

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User with this email already exists'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User with this username already exists'}), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        phone_number=data['phone_number']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200
