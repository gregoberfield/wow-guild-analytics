"""
WSGI entry point for production deployment with Gunicorn.

This module provides the WSGI application callable that Gunicorn expects.
It creates the Flask application instance using the production configuration.

Usage with Gunicorn:
    gunicorn -c gunicorn.conf.py wsgi:app

For development, continue using:
    flask run
"""
from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    # This allows running the app directly for testing
    # In production, Gunicorn will use the 'app' object above
    app.run()
