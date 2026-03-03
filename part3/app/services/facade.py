from app.persistence.repository import (
    UserRepository,
    PlaceRepository,
    ReviewRepository,
    AmenityRepository
)


class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()
