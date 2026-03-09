from typing import Any
from app.models.base_model import BaseModel
from app.extensions import db

class Place(BaseModel):
    __tablename__ = "places"

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), nullable=False)  # FK لاحقًا

    def __init__(self, title: str, price: float, latitude: float, longitude: float, owner_id: str, description: str = "", **kwargs: Any):
        super().__init__(**kwargs)
        self.title = title
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id
        self.description = description
        self.validate()

    def validate(self) -> None:
        if not self.title.strip(): raise ValueError("title required")
        if self.price <= 0: raise ValueError("price must be positive")
        if not (-90 <= self.latitude <= 90): raise ValueError("latitude must be -90..90")
        if not (-180 <= self.longitude <= 180): raise ValueError("longitude must be -180..180")
        if not self.owner_id.strip(): raise ValueError("owner_id required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
