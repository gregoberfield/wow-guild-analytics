from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize SQLAlchemy with engine options if using PostgreSQL
    if hasattr(config_class, 'SQLALCHEMY_ENGINE_OPTIONS'):
        db.init_app(app)
    else:
        db.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Template filters for timestamp formatting
    @app.template_filter('timestamp_to_datetime')
    def timestamp_to_datetime_filter(timestamp):
        """Convert Unix timestamp (seconds) to datetime object"""
        if timestamp:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return None
    
    @app.template_filter('format_relative_time')
    def format_relative_time_filter(dt):
        """Format datetime as relative time (e.g., '2 hours ago', '3 days ago')"""
        if not dt:
            return 'Unknown'
        
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif seconds < 604800:  # Less than 7 days
            days = int(seconds / 86400)
            return f'{days} day{"s" if days != 1 else ""} ago'
        elif seconds < 2592000:  # Less than 30 days
            weeks = int(seconds / 604800)
            return f'{weeks} week{"s" if weeks != 1 else ""} ago'
        elif seconds < 31536000:  # Less than 365 days
            months = int(seconds / 2592000)
            return f'{months} month{"s" if months != 1 else ""} ago'
        else:
            years = int(seconds / 31536000)
            return f'{years} year{"s" if years != 1 else ""} ago'
    
    # Configure logging
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # File handler with rotation (10MB max, keep 5 backup files)
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('WoW Guild Analytics startup')
    
    # Register blueprints
    from app.routes import main_bp
    from app.auth import auth_bp
    from app.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    with app.app_context():
        db.create_all()
        
        # Create default admin user if no users exist
        from app.models import User
        if User.query.count() == 0:
            app.logger.info("No users found. Creating default admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Default admin user created (username: admin, password: admin123)")
            app.logger.warning("IMPORTANT: Change the default admin password immediately!")
    
    return app
