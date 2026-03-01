"""
Test suite for Facility (Amenity) API endpoints.
Tests CRUD operations and authorization rules.
"""
import unittest
import json
from datetime import datetime
from hbnb.app import create_app
from hbnb.app.extensions import db
from hbnb.app.models.user import Account
from hbnb.app.models.amenity import Facility
from flask_jwt_extended import create_access_token


class TestFacilityAPI(unittest.TestCase):
    """Test cases for Facility API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test admin user
        self.admin = Account(
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            plain_password='AdminPass123',
            is_admin=True
        )
        db.session.add(self.admin)
        
        # Create test regular user
        self.user = Account(
            first_name='Regular',
            last_name='User',
            email='user@test.com',
            plain_password='UserPass123',
            is_admin=False
        )
        db.session.add(self.user)
        
        # Create test facility
        self.facility = Facility(
            name='Swimming Pool',
            description='Outdoor heated pool'
        )
        db.session.add(self.facility)
        
        db.session.commit()
        
        # Generate tokens
        self.admin_token = create_access_token(
            identity=self.admin.user_id,
            additional_claims={'is_admin': True}
        )
        
        self.user_token = create_access_token(
            identity=self.user.user_id,
            additional_claims={'is_admin': False}
        )
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    # =====================================================
    # GET /api/v1/amenities - List all facilities
    # =====================================================
    
    def test_get_all_facilities_public(self):
        """Test GET /amenities - public access, no auth required"""
        # Add another facility
        facility2 = Facility(name='WiFi', description='High-speed internet')
        db.session.add(facility2)
        db.session.commit()
        
        response = self.client.get('/api/v1/amenities/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should return both facilities
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        
        # Check structure
        for item in data:
            self.assertIn('id', item)
            self.assertIn('name', item)
            self.assertIn('description', item)
            self.assertIn('created', item)
    
    def test_get_all_facilities_empty(self):
        """Test GET /amenities when no facilities exist"""
        # Delete existing facility
        db.session.delete(self.facility)
        db.session.commit()
        
        response = self.client.get('/api/v1/amenities/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
    
    # =====================================================
    # GET /api/v1/amenities/{id} - Get single facility
    # =====================================================
    
    def test_get_single_facility_success(self):
        """Test GET /amenities/{id} - existing facility"""
        response = self.client.get(f'/api/v1/amenities/{self.facility.facility_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['id'], self.facility.facility_id)
        self.assertEqual(data['name'], 'Swimming Pool')
        self.assertEqual(data['description'], 'Outdoor heated pool')
    
    def test_get_single_facility_not_found(self):
        """Test GET /amenities/{id} - non-existent facility"""
        response = self.client.get('/api/v1/amenities/non-existent-id')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    # =====================================================
    # POST /api/v1/amenities - Create facility (admin only)
    # =====================================================
    
    def test_create_facility_admin_success(self):
        """Test POST /amenities - admin creates facility"""
        new_facility = {
            'name': 'Gym',
            'description': 'Fitness center with modern equipment'
        }
        
        response = self.client.post(
            '/api/v1/amenities/',
            json=new_facility,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'Gym')
        self.assertEqual(data['description'], 'Fitness center with modern equipment')
        
        # Verify in database
        facility = Facility.query.filter_by(facility_name='Gym').first()
        self.assertIsNotNone(facility)
        self.assertEqual(facility.facility_description, 'Fitness center with modern equipment')
    
    def test_create_facility_admin_no_description(self):
        """Test POST /amenities - admin creates facility without description"""
        new_facility = {'name': 'Parking'}
        
        response = self.client.post(
            '/api/v1/amenities/',
            json=new_facility,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        self.assertEqual(data['name'], 'Parking')
        self.assertEqual(data['description'], '')  # Default empty string
    
    def test_create_facility_regular_user_forbidden(self):
        """Test POST /amenities - regular user cannot create facility"""
        new_facility = {'name': 'Gym', 'description': 'Test'}
        
        response = self.client.post(
            '/api/v1/amenities/',
            json=new_facility,
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('Admin privileges required', str(data))
    
    def test_create_facility_unauthorized(self):
        """Test POST /amenities - no auth token"""
        new_facility = {'name': 'Gym', 'description': 'Test'}
        
        response = self.client.post(
            '/api/v1/amenities/',
            json=new_facility
        )
        
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_create_facility_duplicate_name(self):
        """Test POST /amenities - duplicate facility name"""
        new_facility = {'name': 'Swimming Pool'}  # Already exists
        
        response = self.client.post(
            '/api/v1/amenities/',
            json=new_facility,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 409)  # Conflict
        data = json.loads(response.data)
        self.assertIn('already exists', str(data))
    
    def test_create_facility_invalid_data(self):
        """Test POST /amenities - invalid data (name too short)"""
        new_facility = {'name': 'G'}  # Too short (min 2)
        
        response = self.client.post(
            '/api/v1/amenities/',
            json=new_facility,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 400)  # Bad request
    
    # =====================================================
    # PUT /api/v1/amenities/{id} - Update facility (admin only)
    # =====================================================
    
    def test_update_facility_admin_success(self):
        """Test PUT /amenities/{id} - admin updates facility"""
        updates = {
            'name': 'Updated Pool',
            'description': 'Renovated swimming pool'
        }
        
        response = self.client.put(
            f'/api/v1/amenities/{self.facility.facility_id}',
            json=updates,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['name'], 'Updated Pool')
        self.assertEqual(data['description'], 'Renovated swimming pool')
        
        # Verify in database
        db.session.refresh(self.facility)
        self.assertEqual(self.facility.facility_name, 'Updated Pool')
        self.assertEqual(self.facility.facility_description, 'Renovated swimming pool')
    
    def test_update_facility_admin_partial(self):
        """Test PUT /amenities/{id} - admin updates only name"""
        updates = {'name': 'New Name Only'}
        
        response = self.client.put(
            f'/api/v1/amenities/{self.facility.facility_id}',
            json=updates,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['name'], 'New Name Only')
        self.assertEqual(data['description'], 'Outdoor heated pool')  # Unchanged
    
    def test_update_facility_regular_user_forbidden(self):
        """Test PUT /amenities/{id} - regular user cannot update"""
        updates = {'name': 'Hacked Name'}
        
        response = self.client.put(
            f'/api/v1/amenities/{self.facility.facility_id}',
            json=updates,
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_update_facility_not_found(self):
        """Test PUT /amenities/{id} - facility not found"""
        updates = {'name': 'New Name'}
        
        response = self.client.put(
            '/api/v1/amenities/non-existent',
            json=updates,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_facility_duplicate_name(self):
        """Test PUT /amenities/{id} - duplicate name conflict"""
        # Create another facility
        other = Facility(name='Other Facility')
        db.session.add(other)
        db.session.commit()
        
        updates = {'name': 'Other Facility'}  # Trying to use existing name
        
        response = self.client.put(
            f'/api/v1/amenities/{self.facility.facility_id}',
            json=updates,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 409)  # Conflict
    
    # =====================================================
    # DELETE /api/v1/amenities/{id} - Delete facility (admin only)
    # =====================================================
    
    def test_delete_facility_admin_success(self):
        """Test DELETE /amenities/{id} - admin deletes facility"""
        response = self.client.delete(
            f'/api/v1/amenities/{self.facility.facility_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', str(data).lower())
        
        # Verify deleted from database
        deleted = Facility.query.get(self.facility.facility_id)
        self.assertIsNone(deleted)
    
    def test_delete_facility_regular_user_forbidden(self):
        """Test DELETE /amenities/{id} - regular user cannot delete"""
        response = self.client.delete(
            f'/api/v1/amenities/{self.facility.facility_id}',
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_delete_facility_not_found(self):
        """Test DELETE /amenities/{id} - facility not found"""
        response = self.client.delete(
            '/api/v1/amenities/non-existent',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_facility_unauthorized(self):
        """Test DELETE /amenities/{id} - no auth token"""
        response = self.client.delete(f'/api/v1/amenities/{self.facility.facility_id}')
        
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
