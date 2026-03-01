from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app.services.facade import HBnBFacade

api = Namespace('auth', description='Authentication')
facade = HBnBFacade()

# Models
login_model = api.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """User login"""
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Get user by email
        user = facade.get_user_by_email(email)
        if not user or not user.verify_password(password):
            return {'error': 'Invalid credentials'}, 401
        
        # Create tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'is_admin': user.is_admin}
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 200

@api.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token"""
        current_user = get_jwt_identity()
        user = facade.get_user(current_user)
        
        access_token = create_access_token(
            identity=current_user,
            additional_claims={'is_admin': user.is_admin}
        )
        
        return {'access_token': access_token}, 200
