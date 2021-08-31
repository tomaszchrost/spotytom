from flask import Flask
from flask_config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# set to what url_for() should call
login.login_view = 'login'
logging.basicConfig(filename='full.log', encoding='utf-8', level=logging.DEBUG)

from app import routes, models
