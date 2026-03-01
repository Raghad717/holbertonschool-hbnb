from __future__ import annotations

from typing import Any

from hbnb.app.models.base_model import BaseModel
from hbnb.app import db


class Amenity(BaseModel):
    """
    Amenity entity:
    - name (required, max 50)
    - description (optional)
    Relationships:
    - places: many-to-many with Place
    """
    
    __tablename__ = 'amenities'

    # SQLAlchemy columns
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), default="")

    # Relationship (defined in Place model through secondary table)
    # No need to define backref here since it's in Place

    def __init__(self, name: str, description: str = "", **kwargs: Any):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.validate()

    def validate(self) -> None:
        """Validate amenity attributes"""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name is required")
        if len(self.name) > 50:
            raise ValueError("name must be at most 50 characters")
        
        if not isinstance(self.description, str):
            raise ValueError("description must be a string")

    def to_dict(self) -> dict[str, Any]:
        """Convert amenity to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
