from flask_restx import Api
from .users import api as users_ns
from .places import api as places_ns
from .amenities import api as amenities_ns
from .reviews import api as reviews_ns

# Create the API object
api_v1 = Api(
    title="HBnB API",
    version="1.0",
    description="REST API for HBnB project (v1)"
)

# Register all namespaces
api_v1.add_namespace(users_ns, path="/users")
api_v1.add_namespace(places_ns, path="/places")
api_v1.add_namespace(amenities_ns, path="/amenities")
api_v1.add_namespace(reviews_ns, path="/reviews")
