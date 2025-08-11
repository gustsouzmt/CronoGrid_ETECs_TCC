from os import path, getenv
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))

load_dotenv()

class Config:
    SECRET_KEY = getenv('SECRET_KEY', "Senha-Exemplo")

    
    FLASK_MAIL_USERNAME= getenv('MAIL_USERNAME')
    FLASK_MAIL_SENDER = getenv('MAIL_SENDER', 'Exemplo')
    FLASK_MAIL_PASSWORD = getenv('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_NAME')}"
   
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 


class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
