#!/usr/bin/python3
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from app.extensions import bcrypt
from app.persistence.repository import UserRepository, PlaceRepository, ReviewRepository, AmenityRepository

class HBnBFacade:
    def __init__(self):
        self.users = UserRepository()
        self.places = PlaceRepository()
        self.reviews = ReviewRepository()
        self.amenities = AmenityRepository()

    # ---------------- USERS ----------------
    def create_user(self, data: dict):
        user = User(first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'])
        user.set_password(data['password'])
        self.users.create(user)
        return {
            "id": user.id,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }, 201

    def get_all_users(self):
        return [u.to_dict() for u in self.users.get_all()]

    # ---------------- PLACES ----------------
    def create_place(self, user_id: str, **data):
        place = Place(title=data['name'],
                      price=data.get('price', 0.0),
                      latitude=data.get('latitude', 0.0),
                      longitude=data.get('longitude', 0.0),
                      owner_id=user_id,
                      description=data.get('description', ""))
        self.places.create(place)
        return place.to_dict()

    def get_places_by_user(self, user_id: str):
        user = self.users.get_by_id(user_id)
        return [p.to_dict() for p in user.places] if user else []

    # ---------------- REVIEWS ----------------
    def create_review(self, user_id: str, **data):
        review = Review(text=data['text'],
                        rating=data['rating'],
                        user_id=user_id,
                        place_id=data['place_id'])
        self.reviews.create(review)
        return review.to_dict()

    def get_reviews_for_place(self, place_id: str):
        place = self.places.get_by_id(place_id)
        return [r.to_dict() for r in place.reviews] if place else []

    # ---------------- AMENITIES ----------------
    def create_amenity(self, **data):
        amenity = Amenity(name=data['name'], description=data.get('description', ""))
        self.amenities.create(amenity)
        return amenity.to_dict()

    def get_amenities_for_place(self, place_id: str):
        place = self.places.get_by_id(place_id)
        return [a.to_dict() for a in place.amenities] if place else []

# singleton instance
facade = HBnBFacade()
