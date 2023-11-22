from flask import Flask
from main.config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_msearch import Search

app = Flask(__name__, instance_relative_config=False)
app.config.from_object(Config)

db = SQLAlchemy(app)

search = Search(app, db=db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'