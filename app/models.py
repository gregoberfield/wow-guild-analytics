from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Guild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    realm = db.Column(db.String(100), nullable=False)
    faction = db.Column(db.String(20))
    member_count = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('Character', backref='guild', lazy=True)
    history_logs = db.relationship('GuildMemberHistory', backref='guild', lazy=True, order_by='GuildMemberHistory.timestamp.desc()')
    progression_logs = db.relationship('CharacterProgressionHistory', backref='guild', lazy=True, order_by='CharacterProgressionHistory.timestamp.desc()')

class GuildMemberHistory(db.Model):
    """Track member additions and removals from guilds"""
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=False)
    character_name = db.Column(db.String(100), nullable=False)
    character_level = db.Column(db.Integer)
    character_class = db.Column(db.String(50))
    action = db.Column(db.String(20), nullable=False)  # 'added' or 'removed'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<GuildMemberHistory {self.character_name} {self.action} at {self.timestamp}>'

class CharacterProgressionHistory(db.Model):
    """Track character level and item level progression over time"""
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=False)
    character_level = db.Column(db.Integer)
    average_item_level = db.Column(db.Integer)
    equipped_item_level = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<CharacterProgressionHistory char_id={self.character_id} level={self.character_level} ilvl={self.average_item_level} at {self.timestamp}>'

class Task(db.Model):
    """Track background task status for guild syncs and other long-running operations"""
    id = db.Column(db.Integer, primary_key=True)
    celery_id = db.Column(db.String(155), unique=True, nullable=False, index=True)  # Celery task UUID
    task_type = db.Column(db.String(50), nullable=False)  # 'guild_sync', 'character_sync', etc.
    status = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=True)
    progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    current_step = db.Column(db.String(200))  # Current operation description
    result_message = db.Column(db.Text)  # Success message
    error_message = db.Column(db.Text)  # Error details if failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert task to dictionary for API responses"""
        return {
            'id': self.id,
            'celery_id': self.celery_id,
            'task_type': self.task_type,
            'status': self.status,
            'guild_id': self.guild_id,
            'progress': self.progress,
            'current_step': self.current_step,
            'result_message': self.result_message,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': (self.completed_at - self.started_at).total_seconds() if self.completed_at and self.started_at else None
        }
    
    def __repr__(self):
        return f'<Task {self.celery_id} {self.task_type} {self.status}>'

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bnet_id = db.Column(db.BigInteger, index=True)  # Battle.net character ID
    name = db.Column(db.String(100), nullable=False)
    realm = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer)
    character_class = db.Column(db.String(50))
    race = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    faction = db.Column(db.String(20))
    achievement_points = db.Column(db.Integer)
    average_item_level = db.Column(db.Integer)
    equipped_item_level = db.Column(db.Integer)
    spec_name = db.Column(db.String(50))
    rank = db.Column(db.Integer)
    last_login_timestamp = db.Column(db.BigInteger)  # Unix timestamp in milliseconds from Blizzard API
    avatar_url = db.Column(db.String(500))  # Character avatar image URL from Battle.net media endpoint
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=True)
    progression_history = db.relationship('CharacterProgressionHistory', backref='character', lazy=True, order_by='CharacterProgressionHistory.timestamp.desc()', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'realm': self.realm,
            'level': self.level,
            'character_class': self.character_class,
            'race': self.race,
            'gender': self.gender,
            'faction': self.faction,
            'achievement_points': self.achievement_points,
            'average_item_level': self.average_item_level,
            'equipped_item_level': self.equipped_item_level,
            'spec_name': self.spec_name,
            'rank': self.rank,
            'last_login_timestamp': self.last_login_timestamp,
            'avatar_url': self.avatar_url,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

