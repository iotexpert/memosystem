import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskext.markdown import Markdown

from docmgr.extensions import ldap
from docmgr.config import Config

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
    app.config["LDAP_SCHEMA"] = os.getenv('LDAP_SCHEMA')
    app.config["LDAP_PORT"] = os.getenv('LDAP_PORT')
    app.config["LDAP_HOST"] = os.getenv('LDAP_HOST')
    app.config["LDAP_BASE_DN"] = os.getenv('LDAP_BASE_DN')
    app.config["LDAP_USERNAME"] = os.getenv('LDAP_USERNAME')
    app.config["LDAP_PASSWORD"] = os.getenv('LDAP_PASSWORD')
    app.config["LDAP_USER_OBJECT_FILTER"] = os.getenv('LDAP_USER_OBJECT_FILTER')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    if ldap:
        ldap.init_app(app)

    from docmgr.users.routes import users
    from docmgr.main.routes import main
    from docmgr.memos.routes import memos
    from docmgr.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(memos)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app

