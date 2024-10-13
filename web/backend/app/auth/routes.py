from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify
from ..models import User
from .. import db
from flask import Blueprint
from flask_jwt_extended import create_access_token

auth = Blueprint("auth", __name__)

# Логика логина
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if user and check_password_hash(user.password, data.get("password")):
        # Создаем токен, передавая user.id как identity
        token = create_access_token(identity=user.id)
        return jsonify({"token": token}), 200
    
    return jsonify({"message": "Invalid credentials"}), 401


# Логика регистрации
@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Хешируем пароль
    hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
    
    # Создаем нового пользователя
    new_user = User(
        username=data["username"],
        email=data["email"],
        password=hashed_password
    )

    try:
        # Пытаемся добавить пользователя в базу данных
        db.session.add(new_user)
        db.session.commit()
        
        # Создаем токен для нового пользователя
        token = create_access_token(identity=new_user.id)
        return jsonify({"token": token}), 201

    except Exception as e:
        # Обрабатываем ситуацию, если пользователь с таким email уже существует
        db.session.rollback()
        return jsonify({"message": "This user already exists"}), 400
