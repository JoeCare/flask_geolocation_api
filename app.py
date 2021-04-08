import connexion
from connexion.resolver import RestyResolver
import os
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

conned_app = connexion.FlaskApp(__name__, specification_dir=BASE_DIR)
conned_app.add_api('openapi.yaml', resolver=RestyResolver('run'))
app = conned_app.app

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace(
    "://", "ql://", 1)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
mm = Marshmallow(app)

# conned_app.add_api('openapi.yaml')
# conned_app.add_url_rule("/api/v1/", 'main', main_page)

if __name__ == '__main__':
    # init_db()
    # conned_app.add_api('openapi.yaml', resolver=RestyResolver('run'))
    # conned_app.run(host='127.0.0.1', port=5000, debug=True)
    # port = int(os.environ.get('PORT', 5000))
    # conned_app.run(host='0.0.0.0', port=port, debug=False)
    conned_app.run()
