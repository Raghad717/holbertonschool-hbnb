import unittest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.place import Place

class TestReviews(unittest.TestCase):

    def setUp(self):
        self.app = create_app("development")
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            user = User(
                first_name="Reviewer",
                last_name="User",
                email="review@test.com"
            )
            user.set_password("123456")

            db.session.add(user)
            db.session.commit()

            self.user_id = user.id

            place = Place(
                title="Test Place",
                description="Nice place",
                price=100,
                owner_id=self.user_id
            )

            db.session.add(place)
            db.session.commit()

            self.place_id = place.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def get_token(self):
        response = self.client.post("/api/v1/login", json={
            "email": "review@test.com",
            "password": "123456"
        })
        return response.get_json()["access_token"]

    def test_create_review_requires_auth(self):
        response = self.client.post(
            f"/api/v1/places/{self.place_id}/reviews",
            json={
                "text": "Great!",
                "rating": 5
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_owner_cannot_review_own_place(self):
        token = self.get_token()

        response = self.client.post(
            f"/api/v1/places/{self.place_id}/reviews",
            json={
                "text": "My own place",
                "rating": 5
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 400)
