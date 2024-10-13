from flask import request, jsonify, Blueprint, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from . import db
from .models import ChatSession, Message
import requests

main = Blueprint("main", __name__)

# Создание новой сессии чата
@main.route("/api/chat", methods=["POST"])
@jwt_required()
def create_chat_session():
    user_id = get_jwt_identity()
    session_name = request.json.get("session_name")
    
    new_session = ChatSession(user_id=user_id, session_name=session_name, created_at=datetime.now())
    db.session.add(new_session)
    db.session.commit()

    return jsonify({"message": "Chat session created", "session_id": new_session.id}), 201


# Получение всех сессий чатов пользователя
@main.route("/api/chats", methods=["GET"])
@jwt_required()
def get_user_chats():
    user_id = get_jwt_identity()
    
    chat_sessions = ChatSession.query.filter_by(user_id=user_id).all()
    chat_list = [
        {"id": chat.id, "session_name": chat.session_name, "created_at": chat.created_at} 
        for chat in chat_sessions
    ]
    
    return jsonify(chat_list), 200


@main.route("/api/chats/<int:chat_id>", methods=["GET"])
@jwt_required()
def get_chat_history(chat_id):
    user_id = get_jwt_identity()
    
    chat_session = ChatSession.query.filter_by(id=chat_id, user_id=user_id).first()
    if not chat_session:
        return jsonify({"message": "Chat session not found"}), 404

    messages = Message.query.filter_by(chat_session_id=chat_id).all()
    message_list = [
        {"sender": msg.sender, "content": msg.content, "timestamp": msg.timestamp}
        for msg in messages
    ]
    
    return jsonify({"messages": message_list}), 200

@main.route("/api/chats/<int:chat_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(chat_id):
    user_id = get_jwt_identity()  # Получаем ID пользователя
    
    # Проверяем, существует ли сессия чата для текущего пользователя
    chat_session = ChatSession.query.filter_by(id=chat_id, user_id=user_id).first()
    if not chat_session:
        return jsonify({"message": "Chat session not found"}), 404

    # Удаляем все связанные сообщения
    messages = Message.query.filter_by(chat_session_id=chat_id).all()
    for message in messages:
        db.session.delete(message)

    # Удаляем саму сессию чата
    db.session.delete(chat_session)
    db.session.commit()

    return jsonify({"message": "Chat session deleted successfully."}), 200



@main.route("/api/message", methods=["POST"])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()  # Получаем ID пользователя
    chat_session_id = request.json.get("session_id")  # ID сессии
    user_message = request.json.get("message")  # Сообщение пользователя

    # Проверяем, передан ли session_id
    if not chat_session_id:
        return jsonify({"message": "Chat session not found"}), 404

    # Находим сессию чата
    chat_session = ChatSession.query.filter_by(id=chat_session_id, user_id=user_id).first()
    if not chat_session:
        return jsonify({"message": "Chat session not found"}), 404

    # Сохраняем сообщение пользователя
    new_message = Message(
        chat_session_id=chat_session_id, 
        sender="User", 
        content=user_message, 
        timestamp=datetime.now()
    )
    db.session.add(new_message)

    # Логика ответа бота
    bot_response = "Ответ от бота на ваше сообщение."

    # Сохраняем ответ бота
    bot_message = Message(
        chat_session_id=chat_session_id, 
        sender="Bot", 
        content=bot_response, 
        timestamp=datetime.now()
    )
    db.session.add(bot_message)
    
    db.session.commit()

    return jsonify({
        "user_message": user_message,
        "bot_response": bot_response
    }), 201

@main.route("/api/stream", methods=["POST"])
@jwt_required()
def stream_response():
    user_id = get_jwt_identity()
    chat_session_id = request.json.get("session_id")
    user_message = request.json.get("message")

    if not chat_session_id:
        return jsonify({"message": "Chat session not found"}), 404

    chat_session = ChatSession.query.filter_by(id=chat_session_id, user_id=user_id).first()
    if not chat_session:
        return jsonify({"message": "Chat session not found"}), 404

    # Сохраняем сообщение пользователя в базе
    new_message = Message(
        chat_session_id=chat_session_id, 
        sender="User", 
        content=user_message, 
        timestamp=datetime.now()
    )
    db.session.add(new_message)
    db.session.commit()

    # Запрос к модели, которая стримит ответ
    model_url = "http://176.109.100.141:5000/stream"
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
    }
    payload = {'message': user_message}

    # Стриминг ответа от модели
    model_response = requests.post(model_url, headers=headers, json=payload, stream=True)

    # Генерация ответа через stream_with_context
    @stream_with_context
    def generate():
        bot_response = ''
        for chunk in model_response.iter_content(chunk_size=1024):
            data = chunk.decode('utf-8')
            bot_response += data
            yield data

        # Сохранение ответа бота в базе данных после завершения стрима
        bot_message = Message(
            chat_session_id=chat_session_id, 
            sender="Bot", 
            content=bot_response, 
            timestamp=datetime.now()
        )
        db.session.add(bot_message)
        db.session.commit()

    return Response(generate(), content_type='text/plain')


@main.route("/api/more", methods=["POST"])
@jwt_required()
def more_response():
    user_id = get_jwt_identity()
    chat_session_id = request.json.get("session_id")
    user_message = request.json.get("message")

    if not chat_session_id:
        return jsonify({"message": "Chat session not found"}), 404

    chat_session = ChatSession.query.filter_by(id=chat_session_id, user_id=user_id).first()
    if not chat_session:
        return jsonify({"message": "Chat session not found"}), 404

    # Сохраняем сообщение пользователя в базе
    new_message = Message(
        chat_session_id=chat_session_id, 
        sender="User", 
        content=user_message, 
        timestamp=datetime.now()
    )
    db.session.add(new_message)
    db.session.commit()

    # Запрос к модели, которая стримит ответ
    model_url = "http://176.109.100.141:5000/more"
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
    }
    payload = {'message': user_message}

    # Стриминг ответа от модели
    model_response = requests.post(model_url, headers=headers, json=payload, stream=True)

    # Генерация ответа через stream_with_context
    @stream_with_context
    def generate():
        bot_response = ''
        for chunk in model_response.iter_content(chunk_size=1024):
            data = chunk.decode('utf-8')
            bot_response += data
            yield data

        # Сохранение ответа бота в базе данных после завершения стрима
        bot_message = Message(
            chat_session_id=chat_session_id, 
            sender="Bot", 
            content=bot_response, 
            timestamp=datetime.now()
        )
        db.session.add(bot_message)
        db.session.commit()

    return Response(generate(), content_type='text/plain')