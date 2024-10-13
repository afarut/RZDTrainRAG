import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard_to_guess_string"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "postgresql://username:password@db:5432/dbname"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
