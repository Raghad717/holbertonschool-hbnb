#!/usr/bin/python3

from __future__ import annotations

from typing import Any

from app.extensions import db
from .base_model import BaseModel


class Review(BaseModel):
    """
    Review entity with SQLAlchemy mapping.
    
    Attributes:
        text (str): Content of the review (required)
        rating (int): Rating from 1 to 5 (required)
    """
    
    __tablename__ = 'reviews'

    # ==================== TASK 7: SQLAlchemy Columns ====================
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    # ==================== TASK 8: Foreign Keys - Amaal ====================
    user_id  = db.Column(db.String(36), db.ForeignKey('users.id'),  nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a new Review with validation.
        
        Raises:
            ValueError: If validation fails for any field
        """
        super().__init__(**kwargs)

        # ============= Validation =============
        # Text validation
        if not self.text or not self.text.strip():
            raise ValueError("text is required")
        if len(self.text) > 500:
            raise ValueError("text must be under 500 characters")
        self.text = self.text.strip()

        # Rating validation
        if self.rating is None:
            raise ValueError("rating is required")
        try:
            rating_int = int(self.rating)
            if rating_int < 1 or rating_int > 5:
                raise ValueError("rating must be between 1 and 5")
            self.rating = rating_int
        except (TypeError, ValueError):
            raise ValueError("rating must be an integer between 1 and 5")

    # ============= Serialization =============

    def to_dict(self) -> dict:    #ُTask 8, Amaal
        base_dict = super().to_dict()
        base_dict.update({
            "text":     self.text,
            "rating":   self.rating,
            "user_id":  self.user_id,
            "place_id": self.place_id,
        })
        return base_dict

    # ============= Magic Methods =============

    def __str__(self) -> str:
        return f"[Review] {self.rating}/5"

    def __repr__(self) -> str:
        return f"<Review id={self.id} rating={self.rating}>"
