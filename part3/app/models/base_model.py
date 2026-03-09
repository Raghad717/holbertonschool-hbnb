import uuid
from datetime import datetime
from app.extensions import db

class BaseModel(db.Model):
    """Base class for all SQLAlchemy models"""
    
    __abstract__ = True  # prevent SQLAlchemy from creating table for BaseModel

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        """String representation of the model"""
        return f"<{self.__class__.__name__} id={self.id}>"

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
