from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.place import Place
from app.extensions import db

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
