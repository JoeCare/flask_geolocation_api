from flask import Flask, request
import os, connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

conned_app = connexion.App(__name__, specification_dir=BASE_DIR)
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
app.config['SECRET_KEY'] = "flapi"
db = SQLAlchemy(app)

mm = Marshmallow(app)

# AUTH:
#=======================


TOKENS = {
    '123': 'jdoe',
    '456': 'rms'
}


def get_tokeninfo() -> dict:
    try:
        _, access_token = request.headers['Authorization'].split()
        print(access_token)
    except KeyError:
        access_token = ''

    uid = TOKENS.get(access_token)

    if not uid:
        return {401: 'Token not found'}

    return {'uid': uid, 'scope': ['uid']}


def get_secret(user) -> str:
    return 'You are: {uid}'.format(uid=user)
