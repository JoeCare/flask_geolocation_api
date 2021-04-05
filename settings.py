import os, connexion
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

conned_app = connexion.FlaskApp(__name__, specification_dir=BASE_DIR)
app = conned_app.app
# app = Flask('flask_geolocation_api')
# app = Flask(__name__.split('.')[0])

ENV = os.getenv('FLASK_ENV')
if ENV:
    print('dwa razy wczytalam settsy.py',ENV)
else:
    ENV = 'development'
if ENV == 'development':
    app.config['ENV'] = 'development'
    app.debug = True
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    #     BASE_DIR, 'geo.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:m4mp0stgr3s@localhost:5432/postgres"
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True
app.config['CSRF_SESSION_KEY'] = os.getenv('CSRF_SESSION_KEY')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
