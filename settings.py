from flask import Flask, request
import os, connexion
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
load_dotenv(find_dotenv())
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

conned_app = connexion.FlaskApp(__name__, specification_dir=BASE_DIR)
app = conned_app.app
# app = Flask('flask_geolocation_api')
# app = Flask(__name__.split('.')[0])

ENV = 'development'
if ENV == 'development':
    app.config['ENV'] = 'development'
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
        BASE_DIR, 'geo.db')
    # app.config['SQLALCHEMY_DATABASE_URI'] = \
    #     'postgresql://postgres:flapi@localhost'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True
app.config['CSRF_SESSION_KEY'] = "flapi"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
mm = Marshmallow(app)
