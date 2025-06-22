from secrets import token_hex
from os import path, getenv
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))

load_dotenv()

class Config:
    SECRET_KEY = token_hex(32)
    FLASK_MAIL_SUBJECT_PREFIX = ''
    FLASK_MAIL_SENDER = getenv('FLASK_MAIL_SENDER')
    FLASK_MAIL_PASSWORD = getenv('FLASK_MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_NAME')}"
    SQLACLHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
