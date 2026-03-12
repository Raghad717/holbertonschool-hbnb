from flask import Blueprint
from flask_restx import Api, Resource, fields
from flask_jwt_extended import create_access_token
from app.services.facade import facade

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
api = Api(auth_bp)

login_model = api.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True),
})

token_model = api.model('Token', {
    'access_token': fields.String(),
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    @api.response(200, 'Login successful', token_model)
    @api.response(401, 'Invalid credentials')
    def post(self):
        credentials = api.payload
        user = facade.get_user_by_email(credentials['email'])
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401
        access_token = create_access_token(identity=str(user.id),
                                           additional_claims={'is_admin': user.is_admin})
        return {'access_token': access_token}, 200
