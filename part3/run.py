#!/usr/bin/python3
"""HBnB Part 3 entry point"""
import os
from app import create_app
from config import DevelopmentConfig

def setup_database_if_needed(app):
    """Set up the database if it doesn't exist or is empty"""
    from app.extensions import db
    from app.models.user import User

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Check if we have any users (indicating database is populated)
        if User.query.count() == 0:
            print("Database is empty. Running setup...")
            # Import and run the setup function
            from setup_database import main
            main()
        else:
            print("Database already populated.")

app = create_app(DevelopmentConfig)
print("DB URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("instance_path:", app.instance_path)

# Set up database if needed
setup_database_if_needed(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
