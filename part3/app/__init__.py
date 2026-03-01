from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize extensions
bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

def create_app(config_class=Config):
    """Application factory with configuration"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    
    # Register blueprints
    from app.api.v1 import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # JWT configuration
    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        return user_id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        from app.models.user import User
        return User.query.get(identity)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
