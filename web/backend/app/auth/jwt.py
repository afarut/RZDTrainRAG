import jwt
from datetime import datetime, timedelta

SECRET_KEY = "hard_to_guess_string"


def create_jwt_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_jwt_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
