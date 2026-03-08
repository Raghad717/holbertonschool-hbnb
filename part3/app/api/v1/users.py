from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt_identity

# Namespace (this must match what __init__.py imports)
users_bp = Namespace('users', description='User operations')

facade = HBnBFacade()

# Model for API documentation
user_model = users_bp.model('User', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})


@users_bp.route('/')
class UserList(Resource):

    @users_bp.expect(user_model)
    def post(self):
        """Create a new user"""
        data = request.get_json()

        response, status = facade.create_user(data)

        return response, status
