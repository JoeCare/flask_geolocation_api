import connexion, os
from connexion.resolver import RestyResolver
from flask import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


# Globally accessible libraries
db = SQLAlchemy()
mm = Marshmallow()


def init_app():
    """Initialize the Connexion application."""
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    openapi_path = os.path.join(BASE_DIR, "../")
    conn_app = connexion.FlaskApp(
        __name__, specification_dir=openapi_path, options={
            "swagger_ui": True,
            "serve_spec": True
            }
        )
    conn_app.add_api("openapi.yaml", resolver=RestyResolver('run'),
                     strict_validation=True)
    # Flask app and getting into app_context
    app = conn_app.app

    # Load application config
    app.config.from_object('config.ProdConfig')
    app.json_encoder = json.JSONEncoder

    # Initialize Plugins
    db.init_app(app)
    mm.init_app(app)

    with app.app_context():
        # Include our Routes/views
        import run

        # Register Blueprints
        # app.register_blueprint(auth.auth_bp)
        # app.register_blueprint(admin.admin_bp)

        return app
