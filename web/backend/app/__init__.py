from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    from .routes import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .auth.routes import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
