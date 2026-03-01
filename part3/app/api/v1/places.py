"""Place management endpoints for the HBnB platform"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from hbnb.app.services.facade import HBnBFacade

# Create namespace for place operations
place_namespace = Namespace('places', description='Accommodation resource management')

# Initialize service facade
service_facade = HBnBFacade()

def verify_admin_privileges():
    """Check if authenticated user has administrator rights"""
    token_claims = get_jwt()
    return token_claims.get('is_admin', False)

# Request validation schema for place creation/update
place_input_schema = place_namespace.model('PlaceInput', {
    'title': fields.String(
        required=True, 
        description='Property title',
        min_length=3, 
        max_length=100,
        example='Cozy Beachfront Apartment'
    ),
    'description': fields.String(
        description='Property description',
        default='',
        example='Beautiful apartment with ocean view'
    ),
    'price': fields.Float(
        required=True, 
        description='Nightly rate in USD',
        min=1.0,
        example=99.99
    ),
    'latitude': fields.Float(
        required=True, 
        description='Geographic latitude coordinate',
        min=-90, 
        max=90,
        example=40.7128
    ),
    'longitude': fields.Float(
        required=True, 
        description='Geographic longitude coordinate',
        min=-180, 
        max=180,
        example=-74.0060
    ),
    'owner_id': fields.String(
        required=True, 
        description='Property owner identifier',
        example='user-123-abc'
    ),
    'amenities': fields.List(
        fields.String, 
        description='Collection of amenity identifiers',
        default=[],
        example=['amenity-1', 'amenity-2']
    )
})

# Nested model for owner information in responses
owner_info_schema = place_namespace.model('OwnerInfo', {
    'identifier': fields.String(attribute='id', description='Owner system ID'),
    'first_name': fields.String(description='Owner given name'),
    'last_name': fields.String(description='Owner family name'),
    'email_address': fields.String(attribute='email', description='Owner email contact')
})

# Nested model for amenity information in responses
amenity_info_schema = place_namespace.model('PlaceAmenityInfo', {
    'identifier': fields.String(attribute='id', description='Amenity system ID'),
    'display_name': fields.String(attribute='name', description='Amenity display name')
})

# Response schema for place data
place_output_schema = place_namespace.model('PlaceOutput', {
    'identifier': fields.String(attribute='id', description='Place system ID'),
    'property_title': fields.String(attribute='title', description='Property title'),
    'property_description': fields.String(attribute='description', description='Property description'),
    'nightly_rate': fields.Float(attribute='price', description='Nightly rate'),
    'location_latitude': fields.Float(attribute='latitude', description='Latitude coordinate'),
    'location_longitude': fields.Float(attribute='longitude', description='Longitude coordinate'),
    'owner_identifier': fields.String(attribute='owner_id', description='Owner ID'),
    'owner_details': fields.Nested(owner_info_schema, attribute='owner', description='Complete owner information'),
    'available_amenities': fields.List(fields.Nested(amenity_info_schema), attribute='amenities', description='Amenities available'),
    'creation_timestamp': fields.String(attribute='created_at', description='Creation timestamp'),
    'modification_timestamp': fields.String(attribute='updated_at', description='Last modification timestamp')
})

@place_namespace.route('/')
class PlaceCollection(Resource):
    """Resource handler for place collection endpoints"""
    
    @place_namespace.doc('retrieve_all_properties')
    @place_namespace.response(200, 'Successfully retrieved property list')
    def get(self):
        """Fetch all registered properties from the system"""
        properties = service_facade.get_all_places()
        
        formatted_collection = []
        for property_item in properties:
            formatted_collection.append({
                'identifier': property_item.id,
                'property_title': property_item.title,
                'property_description': property_item.description,
                'nightly_rate': property_item.price,
                'location_latitude': property_item.latitude,
                'location_longitude': property_item.longitude,
                'owner_identifier': property_item.owner.id,
                'owner_details': {
                    'identifier': property_item.owner.id,
                    'first_name': property_item.owner.first_name,
                    'last_name': property_item.owner.last_name,
                    'email_address': property_item.owner.email
                },
                'available_amenities': [
                    {'identifier': amenity.id, 'display_name': amenity.name}
                    for amenity in property_item.amenities
                ],
                'guest_reviews': [
                    {
                        'identifier': review.id,
                        'review_text': review.text,
                        'rating_value': review.rating,
                        'reviewer_id': review.user.id
                    }
                    for review in property_item.reviews
                ],
                'creation_timestamp': property_item.created_at.isoformat(),
                'modification_timestamp': property_item.updated_at.isoformat()
            })
        
        return formatted_collection, 200
    
    @place_namespace.doc('register_new_property')
    @place_namespace.expect(place_input_schema)
    @place_namespace.response(201, 'Property successfully registered')
    @place_namespace.response(400, 'Invalid request data')
    @place_namespace.response(401, 'Authentication required')
    @place_namespace.response(404, 'Referenced entity not found')
    @jwt_required()
    def post(self):
        """Create a new property listing (authenticated users only)"""
        property_data = place_namespace.payload
        
        # Extract authenticated user identifier
        authenticated_user = get_jwt_identity()
        
        # Verify ownership claim
        if property_data['owner_id'] != authenticated_user:
            place_namespace.abort(401, 'Cannot create property for another user')
        
        # Validate owner existence
        property_owner = service_facade.get_user(property_data['owner_id'])
        if not property_owner:
            place_namespace.abort(404, 'Specified owner not found')
        
        # Validate referenced amenities
        amenity_references = property_data.get('amenities', [])
        validated_amenities = []
        for amenity_id in amenity_references:
            existing_amenity = service_facade.get_amenity(amenity_id)
            if not existing_amenity:
                place_namespace.abort(404, f'Amenity reference {amenity_id} not found')
            validated_amenities.append(existing_amenity)
        
        try:
            new_property = service_facade.create_place(property_data)
            
            response_data = {
                'identifier': new_property.id,
                'property_title': new_property.title,
                'property_description': new_property.description,
                'nightly_rate': new_property.price,
                'location_latitude': new_property.latitude,
                'location_longitude': new_property.longitude,
                'owner_identifier': new_property.owner.id,
                'owner_details': {
                    'identifier': new_property.owner.id,
                    'first_name': new_property.owner.first_name,
                    'last_name': new_property.owner.last_name,
                    'email_address': new_property.owner.email
                },
                'available_amenities': [
                    {'identifier': amenity.id, 'display_name': amenity.name}
                    for amenity in new_property.amenities
                ],
                'creation_timestamp': new_property.created_at.isoformat(),
                'modification_timestamp': new_property.updated_at.isoformat()
            }
            
            return response_data, 201
            
        except ValueError as error:
            place_namespace.abort(400, str(error))

@place_namespace.route('/<property_identifier>')
@place_namespace.param('property_identifier', 'Unique property system ID')
class PropertyInstance(Resource):
    """Resource handler for individual property operations"""
    
    @place_namespace.doc('fetch_single_property')
    @place_namespace.response(200, 'Successfully retrieved property')
    @place_namespace.response(404, 'Property not found')
    def get(self, property_identifier):
        """Retrieve specific property details by ID"""
        target_property = service_facade.get_place(property_identifier)
        
        if not target_property:
            place_namespace.abort(404, 'Property not found in the system')
        
        response_data = {
            'identifier': target_property.id,
            'property_title': target_property.title,
            'property_description': target_property.description,
            'nightly_rate': target_property.price,
            'location_latitude': target_property.latitude,
            'location_longitude': target_property.longitude,
            'owner_identifier': target_property.owner.id,
            'owner_details': {
                'identifier': target_property.owner.id,
                'first_name': target_property.owner.first_name,
                'last_name': target_property.owner.last_name,
                'email_address': target_property.owner.email
            },
            'available_amenities': [
                {'identifier': amenity.id, 'display_name': amenity.name}
                for amenity in target_property.amenities
            ],
            'guest_reviews': [
                {
                    'identifier': review.id,
                    'review_text': review.text,
                    'rating_value': review.rating,
                    'reviewer_id': review.user.id
                }
                for review in target_property.reviews
            ],
            'creation_timestamp': target_property.created_at.isoformat(),
            'modification_timestamp': target_property.updated_at.isoformat()
        }
        
        return response_data, 200
    
    @place_namespace.doc('modify_existing_property')
    @place_namespace.expect(place_input_schema)
    @place_namespace.response(200, 'Property successfully updated')
    @place_namespace.response(400, 'Invalid modification data')
    @place_namespace.response(403, 'Insufficient permissions')
    @place_namespace.response(404, 'Property not found')
    @jwt_required()
    def put(self, property_identifier):
        """Update an existing property (owner or administrator access only)"""
        modification_data = place_namespace.payload
        
        # Extract authenticated user identifier
        authenticated_user = get_jwt_identity()
        
        # Verify property exists
        existing_property = service_facade.get_place(property_identifier)
        if not existing_property:
            place_namespace.abort(404, 'Property not found in the system')
        
        # Debug output for troubleshooting
        print(f"\n[DEBUG] Property Modification:")
        print(f"  Current User: {authenticated_user}")
        print(f"  Property Owner: {existing_property.owner.id}")
        print(f"  Ownership Match: {existing_property.owner.id == authenticated_user}")
        print(f"  Admin Status: {verify_admin_privileges()}")
        
        # Check authorization (owner or administrator)
        is_authorized = (
            str(existing_property.owner.id) == str(authenticated_user) or 
            verify_admin_privileges()
        )
        
        if not is_authorized:
            place_namespace.abort(403, 'Cannot modify property owned by another user')
        
        # Validate owner reference if being updated
        if 'owner_id' in modification_data:
            referenced_owner = service_facade.get_user(modification_data['owner_id'])
            if not referenced_owner:
                place_namespace.abort(404, 'Referenced owner not found')
        
        # Validate amenity references if being updated
        if 'amenities' in modification_data:
            for amenity_id in modification_data['amenities']:
                referenced_amenity = service_facade.get_amenity(amenity_id)
                if not referenced_amenity:
                    place_namespace.abort(404, f'Amenity reference {amenity_id} not found')
        
        try:
            updated_property = service_facade.update_place(property_identifier, modification_data)
            
            response_data = {
                'identifier': updated_property.id,
                'property_title': updated_property.title,
                'property_description': updated_property.description,
                'nightly_rate': updated_property.price,
                'location_latitude': updated_property.latitude,
                'location_longitude': updated_property.longitude,
                'owner_identifier': updated_property.owner.id,
                'owner_details': {
                    'identifier': updated_property.owner.id,
                    'first_name': updated_property.owner.first_name,
                    'last_name': updated_property.owner.last_name,
                    'email_address': updated_property.owner.email
                },
                'available_amenities': [
                    {'identifier': amenity.id, 'display_name': amenity.name}
                    for amenity in updated_property.amenities
                ],
                'creation_timestamp': updated_property.created_at.isoformat(),
                'modification_timestamp': updated_property.updated_at.isoformat()
            }
            
            return response_data, 200
            
        except ValueError as error:
            place_namespace.abort(400, str(error))
    
    @place_namespace.doc('remove_existing_property')
    @place_namespace.response(200, 'Property successfully removed')
    @place_namespace.response(403, 'Insufficient permissions')
    @place_namespace.response(404, 'Property not found')
    @jwt_required()
    def delete(self, property_identifier):
        """Remove a property listing (owner or administrator access only)"""
        # Extract authenticated user identifier
        authenticated_user = get_jwt_identity()
        
        # Verify property exists
        target_property = service_facade.get_place(property_identifier)
        if not target_property:
            place_namespace.abort(404, 'Property not found in the system')
        
        # Check authorization (owner or administrator)
        is_authorized = (
            target_property.owner.id == authenticated_user or 
            verify_admin_privileges()
        )
        
        if not is_authorized:
            place_namespace.abort(403, 'Cannot remove property owned by another user')
        
        # Remove the property
        service_facade.place_repo.delete(property_identifier)
        return {'message': 'Property successfully removed from the system'}, 200
