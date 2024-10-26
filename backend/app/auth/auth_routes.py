import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from backend.app import db
from backend.app.auth.models import User

# 创建 auth 蓝图
auth_bp = Blueprint('auth', __name__)

# 邮箱和密码的正则表达式
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')


@auth_bp.route('/register', methods=['POST'])
def register():
    # 解析JSON请求体
    data = request.get_json()
    print(f"Received data: {data}")  # 打印接收到的数据以调试

    # 检查输入数据是否完整
    if not data or not all(key in data for key in ['username', 'email', 'password', 'phone_number']):
        print("Missing fields")  # 打印缺少的字段信息
        return jsonify({'message': 'Missing username, email, password, or phone number'}), 400

    # 去除字段前后空格，确保数据一致性
    username = data['username'].strip()
    email = data['email'].strip()
    phone_number = data['phone_number'].strip()
    password = data['password'].strip()

    # 验证邮箱格式
    if not EMAIL_REGEX.match(email):
        print("Invalid email format")  # 打印邮箱格式错误
        return jsonify({'message': 'Invalid email format'}), 400

    # 验证密码格式
    if not PASSWORD_REGEX.match(password):
        print("Invalid password format")  # 打印密码格式错误
        return jsonify({
            'message': 'Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character.'
        }), 400

    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(email=email).first():
        print("Email already exists")  # 打印邮箱已存在
        return jsonify({'message': 'User with this email already exists'}), 400

    if User.query.filter_by(username=username).first():
        print("Username already exists")  # 打印用户名已存在
        return jsonify({'message': 'User with this username already exists'}), 400

    # 哈希密码
    hashed_password = generate_password_hash(password, method='sha256')

    # 创建新用户
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        phone_number=phone_number
    )

    # 保存到数据库
    try:
        db.session.add(new_user)
        db.session.commit()
        print("User registered successfully")  # 打印注册成功信息
        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        print(f"Database error: {e}")  # 打印数据库错误信息
        db.session.rollback()
        return jsonify({'message': 'Internal server error'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    # 解析JSON请求体
    data = request.get_json()
    print(f"Received login data: {data}")  # 打印接收到的数据

    # 检查输入数据是否完整
    if not data or not all(key in data for key in ['email', 'password']):
        print("Missing email or password")  # 打印缺少字段信息
        return jsonify({'message': 'Missing email or password'}), 400

    # 去除字段前后空格，确保数据一致性
    email = data['email'].strip()
    password = data['password'].strip()

    # 根据邮箱查找用户
    user = User.query.filter_by(email=email).first()

    # 检查用户是否存在以及密码是否正确
    if not user:
        print("User not found")  # 打印用户未找到信息
        return jsonify({'message': 'Invalid email or password!'}), 401

    if not check_password_hash(user.password_hash, password):
        print("Incorrect password")  # 打印密码错误信息
        return jsonify({'message': 'Invalid email or password!'}), 401

    # 创建访问令牌
    access_token = create_access_token(identity=user.id)
    print("User logged in successfully")  # 打印登录成功信息
    return jsonify({'access_token': access_token}), 200
