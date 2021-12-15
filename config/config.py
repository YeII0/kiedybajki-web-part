import os
from os import path

class Config:
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    JSON_AS_ASCII = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    # SQLALCHEMY_ECHO = True
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("GMAIL_USER")
    MAIL_PASSWORD = os.environ.get("GMAIL_PASSW")
    BABEL_DEFAULT_LOCALE = "pl"
    FLASK_STATIC_DIGEST_GZIP_FILES = False


def get_loggging_config(app):
    return {
        "version": 1
        , "formatters":
        {
            "detailed":
            {
                "format": "[%(asctime)s][%(levelname)s] in %(module)s.%(funcName)s: %(message)s"
                , "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        
        }
        , "handlers":
        {
            "file":
            {
                "class": "logging.handlers.TimedRotatingFileHandler"
                , "filename": path.join(path.dirname(app.root_path), "logs", "error.log")
                , "delay": True
                , "when": "d"
                , "interval": 1
                , "backupCount": 7
                , "formatter": "detailed"
            }
            , "console":
            {
                "class": "logging.StreamHandler"
            }
            , "new_records_task_file":
            {
                "class": "logging.handlers.TimedRotatingFileHandler"
                , "filename": path.join(
                    app.root_path
                    , "tasks"
                    , "new_records_notification"
                    , "logs"
                    , "error.log"
                )
                , "delay": True
                , "when": "d"
                , "interval": 1
                , "backupCount": 7
                , "formatter": "detailed"                
            }
        }
        , "loggers":
        {
            app.logger.name:
            {
                "handlers": ["file"]
            }
            , "new_records_notification_task":
            {
                "handlers": ["new_records_task_file"]
            }
        }
        , "root":
        {
            "handlers": ["console"]
        }
    }