from flask import Flask
import os

app = Flask(__name__)
# app = Flask('flask_geolocation_api')
# app = Flask(__name__.split('.')[0])

ENV = 'development'
if ENV == 'development':
    app.config['ENV'] = 'development'
    app.debug = True
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
        BASE_DIR, 'database.db')
    # app.config['SQLALCHEMY_DATABASE_URI'] = \
    #     'postgresql://postgres:flapi@localhost'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True
app.config['CSRF_SESSION_KEY'] = "flapi"
app.config['SECRET_KEY'] = "flapi"
