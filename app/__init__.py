from os import getenv, path
from flask import Flask, current_app
from flask_moment import Moment
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import config
from dotenv import load_dotenv

moment = Moment()
mail = Mail()
db = SQLAlchemy()

data_file = path.join(path.dirname(__file__), 'static', 'data', 'professores.json')

def create_app(config_name):
    load_dotenv()

    app = Flask(__name__)

    DB_USER = getenv("DB_USER")
    DB_PASSWORD = getenv("DB_PASSWORD")
    DB_HOST = getenv("DB_HOST")
    DB_NAME = getenv("DB_NAME")

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .main import main
    app.register_blueprint(main)

    return app
