import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required
from backend.app import db
from backend.app.auth.models import User

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
MIN_PASSWORD_LENGTH = 8

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing username, email, or password'}), 400

    if not EMAIL_REGEX.match(data['email']):
        return jsonify({'message': 'Invalid email format'}), 400

    if len(data['password']) < MIN_PASSWORD_LENGTH:
        return jsonify({'message': f'Password must be at least {MIN_PASSWORD_LENGTH} characters long'}), 400

    hashed_password = generate_password_hash(data['password'], method='sha256')

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User with this email already exists'}), 400

    new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password, phone_number=data.get('phone_number'))

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/user/<email>', methods=['GET'])
@jwt_required()
def get_user(email):
    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'created_at': user.created_at
        })
    else:
        return jsonify({'message': 'User not found'}), 404
