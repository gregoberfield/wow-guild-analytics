from app import db
from datetime import datetime

class Guild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    realm = db.Column(db.String(100), nullable=False)
    faction = db.Column(db.String(20))
    member_count = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('Character', backref='guild', lazy=True)

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
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=True)
    
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
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
