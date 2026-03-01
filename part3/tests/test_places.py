"""
Test suite for Place (Property) API endpoints.
Tests CRUD operations and authorization rules.
"""
import unittest
import json
from hbnb.app import create_app
from hbnb.app.extensions import db
from hbnb.app.models.user import Account
from hbnb.app.models.place import Property
from hbnb.app.models.amenity import Facility
from flask_jwt_extended import create_access_token


class TestPlaceAPI(unittest.TestCase):
    """Test cases for Property API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test users
        self.owner = Account(
            first_name='Property',
            last_name='Owner',
            email='owner@test.com',
            plain_password='OwnerPass123',
            is_admin=False
        )
        db.session.add(self.owner)
        
        self.other_user = Account(
            first_name='Other',
            last_name='User',
            email='other@test.com',
            plain_password='OtherPass123',
            is_admin=False
        )
        db.session.add(self.other_user)
        
        self.admin = Account(
            first_name='Admin',
            last_name='User',
            email='admin@places.com',
            plain_password='AdminPass123',
            is_admin=True
        )
        db.session.add(self.admin)
        
        # Create test facilities
        self.facility1 = Facility(name='WiFi', description='Internet')
        self.facility2 = Facility(name='Parking', description='Parking space')
        db.session.add_all([self.facility1, self.facility2])
        
        # Create test property
        self.property = Property(
            title='Test Beach House',
            description='Beautiful beachfront property',
            price=199.99,
            latitude=25.7617,
            longitude=-80.1918,
            owner_id=self.owner.user_id
        )
        db.session.add(self.property)
        
        # Link facilities
        self.property.amenities.append(self.facility1)
        
        db.session.commit()
        
        # Generate tokens
        self.owner_token = create_access_token(
            identity=self.owner.user_id,
            additional_claims={'is_admin': False}
        )
        
        self.other_token = create_access_token(
            identity=self.other_user.user_id,
            additional_claims={'is_admin': False}
        )
        
        self.admin_token = create_access_token(
            identity=self.admin.user_id,
            additional_claims={'is_admin': True}
        )
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    # =====================================================
    # GET /api/v1/places - List all properties
    # =====================================================
    
    def test_get_all_properties_public(self):
        """Test GET /places - public access"""
        response = self.client.get('/api/v1/places/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        
        # Check structure
        prop = data[0]
        self.assertIn('id', prop)
        self.assertIn('title', prop)
        self.assertIn('description', prop)
        self.assertIn('price', prop)
        self.assertIn('location_latitude', prop)
        self.assertIn('location_longitude', prop)
        self.assertIn('owner_id', prop)
        self.assertIn('owner_details', prop)
        self.assertIn('available_amenities', prop)
        
        # Check amenities
        self.assertEqual(len(prop['available_amenities']), 1)
        self.assertEqual(prop['available_amenities'][0]['name'], 'WiFi')
    
    # =====================================================
    # GET /api/v1/places/{id} - Get single property
    # =====================================================
    
    def test_get_single_property_success(self):
        """Test GET /places/{id} - existing property"""
        response = self.client.get(f'/api/v1/places/{self.property.property_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['id'], self.property.property_id)
        self.assertEqual(data['title'], 'Test Beach House')
        self.assertEqual(data['price'], 199.99)
    
    def test_get_single_property_not_found(self):
        """Test GET /places/{id} - non-existent property"""
        response = self.client.get('/api/v1/places/non-existent')
        self.assertEqual(response.status_code, 404)
    
    # =====================================================
    # POST /api/v1/places - Create property
    # =====================================================
    
    def test_create_property_success(self):
        """Test POST /places - authenticated user creates property"""
        new_property = {
            'title': 'Mountain Cabin',
            'description': 'Cozy cabin in the woods',
            'price': 299.50,
            'latitude': 39.5501,
            'longitude': -105.7821,
            'owner_id': self.owner.user_id,
            'amenities': [self.facility1.facility_id, self.facility2.facility_id]
        }
        
        response = self.client.post(
            '/api/v1/places/',
            json=new_property,
            headers={'Authorization': f'Bearer {self.owner_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
       
