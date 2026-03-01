"""Initialize Flask extensions."""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

# Database ORM
db = SQLAlchemy()

# JWT authentication
jwt = JWTManager()

# Password hashing
bcrypt = Bcrypt()
