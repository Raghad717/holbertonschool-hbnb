from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.place import Place
from app.extensions import db
from app.models.base_model import BaseModel

class Place(BaseModel):
    __tablename__ = "places"

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"))

@places_bp.route("/", methods=["POST"])
@jwt_required()
def create_place():
    data = request.get_json()
    user_id = get_jwt_identity()

    place = Place(
        title=data["title"],
        description=data["description"],
        price=data["price"],
        owner_id=user_id
    )

    db.session.add(place)
    db.session.commit()

    return {"message": "Place created"}, 201
