import unittest
import json
from app import create_app, db
from app.models.user import User
from flask_jwt_extended import create_access_token

class TestUsers(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        
        self.user = User(
            first_name='Normal',
            last_name='User',
            email='normal@test.com',
            password='password123',
            is_admin=False
        )
        db.session.add(self.user)
        
        
        self.admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            password='admin123',
            is_admin=True
        )
        db.session.add(self.admin)
        db.session.commit()
        
        
        self.user_token = create_access_token(identity=str(self.user.id))
        self.admin_token = create_access_token(identity=str(self.admin.id))
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_user(self):
        
        response = self.client.post('/api/v1/users/',
            json={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'new@test.com',
                'password': 'newpass123'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'new@test.com')
    
    def test_create_user_duplicate_email(self):
     
        response = self.client.post('/api/v1/users/',
            json={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'normal@test.com',  # موجود
                'password': 'password123'
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_user_by_id(self):
        
        response = self.client.get(f'/api/v1/users/{self.user.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'normal@test.com')
        self.assertNotIn('password', data)  
    
    def test_update_own_profile(self):
        
        response = self.client.put(f'/api/v1/users/{self.user.id}',
            json={'first_name': 'Updated'},
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], 'Updated')
    
    def test_update_other_user_forbidden(self):
        
        other_user = User(
            first_name='Other',
            last_name='User',
            email='other@test.com',
            password='pass123'
        )
        db.session.add(other_user)
        db.session.commit()
        
        response = self.client.put(f'/api/v1/users/{other_user.id}',
            json={'first_name': 'Hacked'},
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        self.assertEqual(response.status_code, 403)
    
    def test_admin_update_any_user(self):
        
        response = self.client.put(f'/api/v1/users/{self.user.id}',
            json={'first_name': 'AdminUpdated'},
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], 'AdminUpdated')
    
    def test_admin_delete_user(self):
        
        response = self.client.delete(f'/api/v1/users/{self.user.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
