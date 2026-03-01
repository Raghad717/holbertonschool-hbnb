from __future__ import annotations

import re
from typing import Any

from hbnb.app.models.base_model import BaseModel
from hbnb.app.extensions import bcrypt
from hbnb.app import db

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User(BaseModel):
    """
    SQLAlchemy User Model:
    - first_name (required, max 50)
    - last_name  (required, max 50)
    - email      (required, valid format, unique)
    - password   (required, hashed)
    - is_admin   (bool, default False)
    
    Relationships:
    - places: places owned by this user
    - reviews: reviews written by this user
    """
    
    __tablename__ = 'users'
    
    # SQLAlchemy columns
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column('password', db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships (will be populated by backref in other models)
    # places = db.relationship('Place', backref='owner', lazy=True, cascade='all, delete-orphan')
    # reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str = None,
        is_admin: bool = False,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        
        # Hash password if provided
        if password:
            self.hash_password(password)
        else:
            self.password_hash = ""
            
        self.validate()

    @property
    def password(self):
        """Prevent password from being accessed directly"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, plain_password: str) -> None:
        """Hash password using bcrypt when set"""
        self.hash_password(plain_password)

    def hash_password(self, password: str) -> None:
        """Hash the password using bcrypt"""
        if not password or not isinstance(password, str):
            raise ValueError("password is required and must be a string")
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Verify a password against the hashed password"""
        if not self.password_hash or not password:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    def validate(self) -> None:
        """Validate user attributes"""
        # Validate first_name
        if not isinstance(self.first_name, str) or not self.first_name.strip():
            raise ValueError("first_name is required")
        if len(self.first_name) > 50:
            raise ValueError("first_name must be at most 50 characters")

        # Validate last_name
        if not isinstance(self.last_name, str) or not self.last_name.strip():
            raise ValueError("last_name is required")
        if len(self.last_name) > 50:
            raise ValueError("last_name must be at most 50 characters")

        # Validate email
        if not isinstance(self.email, str) or not self.email.strip():
            raise ValueError("email is required")
        if not _EMAIL_RE.match(self.email.strip()):
            raise ValueError("email must be a valid email address")

        # Validate is_admin
        if not isinstance(self.is_admin, bool):
            raise ValueError("is_admin must be a boolean")

        # Validate password_hash exists
        if not self.password_hash or len(self.password_hash) < 20:
            raise ValueError("password is required and must be properly hashed")

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation without password"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_full(self) -> dict[str, Any]:
        """Return full dictionary with relationships (for admin use)"""
        base_dict = self.to_dict()
        
        # Add relationship data if available
        from hbnb.app.models.place import Place
        from hbnb.app.models.review import Review
        
        # This requires the relationships to be defined
        # Will be populated when Place and Review models are complete
        
        return base_dict
