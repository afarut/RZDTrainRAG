from . import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    chat_sessions = relationship('ChatSession', backref='user', lazy=True)


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    session_name = db.Column(db.String, nullable=True)

    messages = relationship('Message', backref='session', lazy=True)


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    chat_session_id = db.Column(db.Integer, ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(512), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    additional_data = db.Column(JSON, nullable=True)