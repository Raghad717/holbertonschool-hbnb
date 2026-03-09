from flask import Flask
from app.extensions import db, jwt, bcrypt
from app.api.v1 import bp_v1  
from config import config_dict


def create_app(config_name="development"):
    """
    Factory function to create Flask app with:
    - Extensions initialized
    - Blueprint registered
    - Config loaded from config_dict
    """
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register the main API blueprint (v1)
    app.register_blueprint(bp_v1, url_prefix="/api/v1")

    return app
