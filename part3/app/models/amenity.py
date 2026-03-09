from typing import Any
from app.models.base_model import BaseModel
from app.extensions import db

class Amenity(BaseModel):
    __tablename__ = "amenities"

    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), default="")

    def __init__(self, name: str, description: str = "", **kwargs: Any):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.validate()

    def validate(self):
        if not self.name.strip(): raise ValueError("name required")
        if len(self.name) > 50: raise ValueError("name max 50 chars")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
