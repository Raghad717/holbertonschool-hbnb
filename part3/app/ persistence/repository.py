from app.extensions import db
from app.models.base_model import BaseModel

class Place(BaseModel):
    __tablename__ = "places"

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"))
class SQLAlchemyRepository:

    def add(self, obj):
        db.session.add(obj)
        db.session.commit()

    def get(self, model, obj_id):
        return model.query.get(obj_id)

    def get_all(self, model):
        return model.query.all()

    def delete(self, obj):
        db.session.delete(obj)
        db.session.commit()
