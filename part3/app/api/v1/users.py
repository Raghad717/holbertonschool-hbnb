from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.services.facade import HBnBFacade

api = Namespace('users', description='User operations')
facade = HBnBFacade()

# Models
user_model = api.model('User', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'is_admin': fields.Boolean(default=False)
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(),
    'last_name': fields.String()
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model)
    def post(self):
        """Create new user"""
        data = request.json
        
        # Check if email exists
        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400
        
        user = facade.create_user(data)
        return user.to_dict(), 201
    
    def get(self):
        """Get all users"""
        users = facade.get_all_users()
        return [user.to_dict() for user in users], 200

@api.route('/<string:user_id>')
class UserResource(Resource):
    def get(self, user_id):
        """Get user by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200
    
    @jwt_required()
    @api.expect(user_update_model)
    def put(self, user_id):
        """Update user"""
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Check permissions
        if not is_admin and current_user != user_id:
            return {'error': 'Unauthorized'}, 403
        
        data = request.json
        user = facade.update_user(user_id, data)
        if not user:
            return {'error': 'User not found'}, 404
        
        return user.to_dict(), 200
    
    @jwt_required()
    def delete(self, user_id):
        """Delete user (admin only)"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin access required'}, 403
        
        if facade.delete_user(user_id):
            return {'message': 'User deleted'}, 200
        return {'error': 'User not found'}, 404
