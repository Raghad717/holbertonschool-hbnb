"""Review management endpoints for the HBnB platform"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from hbnb.app.services.facade import HBnBFacade

class Review(BaseModel):
    __tablename__ = "reviews"

    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    place_id = db.Column(db.String(36), db.ForeignKey("places.id"))
# Create namespace for review operations
review_namespace = Namespace('reviews', description='Guest feedback management')

# Initialize service facade
service_facade = HBnBFacade()

def verify_admin_privileges():
    """Check if authenticated user has administrator rights"""
    token_claims = get_jwt()
    return token_claims.get('is_admin', False)

# Request validation schema for review creation/update
review_input_schema = review_namespace.model('ReviewInput', {
    'text': fields.String(
        required=True, 
        description='Review content',
        min_length=5,
        example='Great location and wonderful host!'
    ),
    'rating': fields.Integer(
        required=True, 
        description='Numerical rating (1-5 scale)',
        min=1, 
        max=5,
        example=5
    ),
    'user_id': fields.String(
        required=True, 
        description='Review author identifier',
        example='user-123-abc'
    ),
    'place_id': fields.String(
        required=True, 
        description='Target property identifier',
        example='place-456-def'
    )
})

# Nested model for reviewer information in responses
reviewer_info_schema = review_namespace.model('ReviewerInfo', {
    'identifier': fields.String(attribute='id', description='Reviewer system ID'),
    'given_name': fields.String(attribute='first_name', description='Reviewer first name'),
    'family_name': fields.String(attribute='last_name', description='Reviewer last name')
})

# Response schema for review data
review_output_schema = review_namespace.model('ReviewOutput', {
    'identifier': fields.String(attribute='id', description='Review system ID'),
    'review_content': fields.String(attribute='text', description='Review text'),
    'rating_value': fields.Integer(attribute='rating', description='Numerical rating'),
    'author_identifier': fields.String(attribute='user_id', description='Author ID'),
    'property_identifier': fields.String(attribute='place_id', description='Property ID'),
    'author_details': fields.Nested(reviewer_info_schema, attribute='user', description='Complete author information'),
    'creation_timestamp': fields.String(attribute='created_at', description='Creation timestamp'),
    'modification_timestamp': fields.String(attribute='updated_at', description='Last modification timestamp')
})

@review_namespace.route('/')
class ReviewCollection(Resource):
    """Resource handler for review collection endpoints"""
    
    @review_namespace.doc('retrieve_all_feedback')
    @review_namespace.response(200, 'Successfully retrieved feedback list')
    def get(self):
        """Fetch all registered reviews from the system"""
        all_reviews = service_facade.get_all_reviews()
        
        formatted_collection = []
        for review_item in all_reviews:
            formatted_collection.append({
                'identifier': review_item.id,
                'review_content': review_item.text,
                'rating_value': review_item.rating,
                'author_identifier': review_item.user.id,
                'property_identifier': review_item.place.id,
                'author_details': {
                    'identifier': review_item.user.id,
                    'given_name': review_item.user.first_name,
                    'family_name': review_item.user.last_name
                },
                'creation_timestamp': review_item.created_at.isoformat(),
                'modification_timestamp': review_item.updated_at.isoformat()
            })
        
        return formatted_collection, 200
    
    @review_namespace.doc('submit_new_feedback')
    @review_namespace.expect(review_input_schema)
    @review_namespace.response(201, 'Review successfully submitted')
    @review_namespace.response(400, 'Invalid request data')
    @review_namespace.response(401, 'Authentication required')
    @review_namespace.response(403, 'Submission prohibited')
    @review_namespace.response(404, 'Referenced entity not found')
    @jwt_required()
    def post(self):
        """Create a new review (authenticated users only)"""
        review_data = review_namespace.payload
        
        # Extract authenticated user identifier
        authenticated_user = get_jwt_identity()
        
        # Verify authorship claim
        if review_data['user_id'] != authenticated_user:
            review_namespace.abort(401, 'Cannot submit review on behalf of another user')
        
        # Validate author existence
        review_author = service_facade.get_user(review_data['user_id'])
        if not review_author:
            review_namespace.abort(404, 'Specified author not found')
        
        # Validate property existence
        target_property = service_facade.get_place(review_data['place_id'])
        if not target_property:
            review_namespace.abort(404, 'Specified property not found')
        
        # Prevent self-review (owner reviewing own property)
        if target_property.owner.id == authenticated_user:
            review_namespace.abort(403, 'Cannot review your own property')
        
        # Prevent duplicate reviews
        existing_reviews = service_facade.get_reviews_by_place(review_data['place_id'])
        for existing in existing_reviews:
            if existing.user.id == authenticated_user:
                review_namespace.abort(403, 'You have already submitted a review for this property')
        
        try:
            new_review = service_facade.create_review(review_data)
            
            response_data = {
                'identifier': new_review.id,
                'review_content': new_review.text,
                'rating_value': new_review.rating,
                'author_identifier': new_review.user.id,
                'property_identifier': new_review.place.id,
                'author_details': {
                    'identifier': new_review.user.id,
                    'given_name': new_review.user.first_name,
                    'family_name': new_review.user.last_name
                },
                'creation_timestamp': new_review.created_at.isoformat(),
                'modification_timestamp': new_review.updated_at.isoformat()
            }
            
            return response_data, 201
            
        except ValueError as error:
            review_namespace.abort(400, str(error))

@review_namespace.route('/<review_identifier>')
@review_namespace.param('review_identifier', 'Unique review system ID')
class ReviewInstance(Resource):
    """Resource handler for individual review operations"""
    
    @review_namespace.doc('fetch_single_review')
    @review_namespace.response(200, 'Successfully retrieved review')
    @review_namespace.response(404, 'Review not found')
    def get(self, review_identifier):
        """Retrieve specific review details by ID"""
        target_review = service_facade.get_review(review_identifier)
        
        if not target_review:
            review_namespace.abort(404, 'Review not found in the system')
        
        response_data = {
            'identifier': target_review.id,
            'review_content': target_review.text,
            'rating_value': target_review.rating,
            'author_identifier': target_review.user.id,
            'property_identifier': target_review.place.id,
            'author_details': {
                'identifier': target_review.user.id,
                'given_name': target_review.user.first_name,
                'family_name': target_review.user.last_name
            },
            'creation_timestamp': target_review.created_at.isoformat(),
            'modification_timestamp': target_review.updated_at.isoformat()
        }
        
        return response_data, 200
    
    @review_namespace.doc('modify_existing_review')
    @review_namespace.expect(review_input_schema)
    @review_namespace.response(200, 'Review successfully updated')
    @review_namespace.response(400, 'Invalid modification data')
    @review_namespace.response(403, 'Insufficient permissions')
    @review_namespace.response(404, 'Review not found')
    @jwt_required()
    def put(self, review_identifier):
        """Update an existing review (author or administrator access only)"""
        modification_data = review_namespace.payload
        
        # Extract authenticated user identifier
        authenticated_user = get_jwt_identity()
        
        # Verify review exists
        existing_review = service_facade.get_review(review_identifier)
        if not existing_review:
            review_namespace.abort(404, 'Review not found in the system')
        
        # Debug output for troubleshooting
        print(f"\n[DEBUG] Review Modification:")
        print(f"  Current User: {authenticated_user}")
        print(f"  Review Author: {existing_review.user.id}")
        print(f"  Authorship Match: {existing_review.user.id == authenticated_user}")
        print(f"  Admin Status: {verify_admin_privileges()}")
        
        # Check authorization (author or administrator)
        is_authorized = (
            str(existing_review.user.id) == str(authenticated_user) or 
            verify_admin_privileges()
        )
        
        if not is_authorized:
            review_namespace.abort(403, 'Cannot modify review written by another user')
        
        # Validate author reference if being updated
        if 'user_id' in modification_data:
            referenced_author = service_facade.get_user(modification_data['user_id'])
            if not referenced_author:
                review_namespace.abort(404, 'Referenced author not found')
        
        # Validate property reference if being updated
        if 'place_id' in modification_data:
            referenced_property = service_facade.get_place(modification_data['place_id'])
            if not referenced_property:
                review_namespace.abort(404, 'Referenced property not found')
        
        try:
            updated_review = service_facade.update_review(review_identifier, modification_data)
            
            response_data = {
                'identifier': updated_review.id,
                'review_content': updated_review.text,
                'rating_value': updated_review.rating,
                'author_identifier': updated_review.user.id,
                'property_identifier': updated_review.place.id,
                'author_details': {
                    'identifier': updated_review.user.id,
                    'given_name': updated_review.user.first_name,
                    'family_name': updated_review.user.last_name
                },
                'creation_timestamp': updated_review.created_at.isoformat(),
                'modification_timestamp': updated_review.updated_at.isoformat()
            }
            
            return response_data, 200
            
        except ValueError as error:
            review_namespace.abort(400, str(error))
    
    @review_namespace.doc('remove_existing_review')
    @review_namespace.response(200, 'Review successfully removed')
    @review_namespace.response(403, 'Insufficient permissions')
    @review_namespace.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_identifier):
        """Remove a review (author or administrator access only)"""
        # Extract authenticated user identifier
        authenticated_user = get_jwt_identity()
        
        # Verify review exists
        target_review = service_facade.get_review(review_identifier)
        if not target_review:
            review_namespace.abort(404, 'Review not found in the system')
        
        # Check authorization (author or administrator)
        is_authorized = (
            target_review.user.id == authenticated_user or 
            verify_admin_privileges()
        )
        
        if not is_authorized:
            review_namespace.abort(403, 'Cannot remove review written by another user')
        
        # Remove the review
        service_facade.delete_review(review_identifier)
        return {'message': 'Review successfully removed from the system'}, 200

@review_namespace.route('/properties/<property_identifier>/reviews')
@review_namespace.param('property_identifier', 'Unique property system ID')
class PropertyFeedbackCollection(Resource):
    """Resource handler for property-specific review collections"""
    
    @review_namespace.doc('retrieve_property_feedback')
    @review_namespace.response(200, 'Successfully retrieved property reviews')
    @review_namespace.response(404, 'Property not found')
    def get(self, property_identifier):
        """Fetch all reviews for a specific property"""
        target_property = service_facade.get_place(property_identifier)
        if not target_property:
            review_namespace.abort(404, 'Property not found in the system')
        
        property_reviews = service_facade.get_reviews_by_place(property_identifier)
        
        formatted_collection = []
        for review_item in property_reviews:
            formatted_collection.append({
                'identifier': review_item.id,
                'review_content': review_item.text,
                'rating_value': review_item.rating,
                'author_identifier': review_item.user.id,
                'author_details': {
                    'identifier': review_item.user.id,
                    'given_name': review_item.user.first_name,
                    'family_name': review_item.user.last_name
                },
                'creation_timestamp': review_item.created_at.isoformat(),
                'modification_timestamp': review_item.updated_at.isoformat()
            })
        
        return formatted_collection, 200
