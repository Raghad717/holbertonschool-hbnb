import unittest
import json
from app import create_app, db
from app.models.user import User

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        user = User(
            first_name='Test',
            last_name='User',
            email='test@test.com',
            password='password123',
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_success(self):
        response = self.client.post(
            '/api/v1/auth/login',
            json={'email': 'test@test.com', 'password': 'password123'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
    
    def test_login_wrong_password(self):
        response = self.client.post(
            '/api/v1/auth/login',
            json={'email': 'test@test.com', 'password': 'wrong'}
        )
        self.assertEqual(response.status_code, 401)
    
    def test_login_user_not_found(self):
        response = self.client.post(
            '/api/v1/auth/login',
            json={'email': 'notfound@test.com', 'password': 'password123'}
        )
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
