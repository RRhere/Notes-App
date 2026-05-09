import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()

mail = Mail()

DB_NAME = "temp1.db"


def create_app():

    app = Flask(__name__)

    app.config.from_object("config")

    db.init_app(app)

    mail.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")

    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    with app.app_context():

        db.create_all()

    login_manager = LoginManager()

    login_manager.login_view = "auth.login"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(int(user_id))

    return app