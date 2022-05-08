import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskext.markdown import Markdown

from memos.extensions import ldap
from memos.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    Markdown(app)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    if ldap:
        ldap.init_app(app)

    from memos.users.routes import users
    from memos.main.routes import main
    from memos.memos.routes import memos
    from memos.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(memos)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
