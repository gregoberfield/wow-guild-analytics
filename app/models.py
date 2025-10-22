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
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
