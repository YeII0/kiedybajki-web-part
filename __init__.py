import logging
import logging.config
import os
from os import path
import yaml
from flask.logging import default_handler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from flask_static_digest import FlaskStaticDigest
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from animechecker.config.config import Config, get_loggging_config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_message = "Zaloguj się aby uzyskać dostęp do tej strony."
login_manager.login_view = 'users_bp.login'
login_manager.login_message_category = 'info'
mail = Mail()
babel = Babel()
flask_static_digest = FlaskStaticDigest()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not path.isdir(path.join(path.dirname(app.root_path), "logs")):
        os.mkdir(path.join(path.dirname(app.root_path), "logs"))

    logging.config.dictConfig(get_loggging_config(app))


    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    flask_static_digest.init_app(app)
    # paranoid.init_app(app)
    csrf.init_app(app)

    from animechecker.users.routes import users_bp
    from animechecker.main.routes import main_bp
    from animechecker.errors.handlers import errors_bp
    from animechecker.admin import admin_bp
    from animechecker.commands import commands_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(commands_bp)

    return app