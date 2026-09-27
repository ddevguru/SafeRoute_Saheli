from datetime import datetime
from backend.app.database import db

class LocationHistory(db.Model):
    """GPS Trail tracking user movements with emergency flag"""
    __tablename__ = 'location_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    device_id = db.Column(db.String(64), nullable=True)
    incident_id = db.Column(db.String(36), db.ForeignKey('emergency_incidents.id', ondelete='SET NULL'), nullable=True, index=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    accuracy = db.Column(db.Float, default=5.0)
    speed = db.Column(db.Float, default=0.0)
    heading = db.Column(db.Float, default=0.0)
    is_emergency = db.Column(db.Boolean, default=False)
    battery_level = db.Column(db.Integer, default=100)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', back_populates='location_points')
    incident = db.relationship('EmergencyIncident', back_populates='location_points')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'incident_id': self.incident_id,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None,
            'accuracy': self.accuracy,
            'speed': self.speed,
            'heading': self.heading,
            'is_emergency': self.is_emergency,
            'battery_level': self.battery_level,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }
