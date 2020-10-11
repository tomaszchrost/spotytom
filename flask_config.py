import os
import authenticator

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or ''
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@localhost/flask'.format(authenticator.db_username, authenticator.db_password)
    SQLALCHEMY_TRACK_MODIFICATIONS = False