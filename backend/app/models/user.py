from datetime import datetime
import bcrypt
from backend.app.database import db, generate_uuid

class User(db.Model):
    """Saheli / Primary Female User Account"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(191), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    profile_photo_url = db.Column(db.String(500), nullable=True)
    emergency_blood_group = db.Column(db.String(10), nullable=True)
    medical_notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Privacy Settings
    privacy_guardian_camera = db.Column(db.Boolean, default=True, nullable=False)
    privacy_emergency_camera_override = db.Column(db.Boolean, default=True, nullable=False)
    privacy_audio_recording = db.Column(db.Boolean, default=True, nullable=False)
    privacy_live_location = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    guardian_links = db.relationship('GuardianUser', back_populates='saheli', cascade='all, delete-orphan')
    devices = db.relationship('Device', back_populates='assigned_user')
    emergency_contacts = db.relationship('EmergencyContact', back_populates='user', cascade='all, delete-orphan')
    incidents = db.relationship('EmergencyIncident', back_populates='user', cascade='all, delete-orphan')
    location_points = db.relationship('LocationHistory', back_populates='user', cascade='all, delete-orphan')
    device_tokens = db.relationship('DeviceToken', back_populates='user', cascade='all, delete-orphan')
    routes = db.relationship('Route', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, plain_password: str) -> None:
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, plain_password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self, include_sensitive: bool = False) -> dict:
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'profile_photo_url': self.profile_photo_url,
            'emergency_blood_group': self.emergency_blood_group,
            'medical_notes': self.medical_notes,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'privacy_settings': {
                'guardian_camera': self.privacy_guardian_camera,
                'emergency_camera_override': self.privacy_emergency_camera_override,
                'audio_recording': self.privacy_audio_recording,
                'live_location': self.privacy_live_location,
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        return data


class EmergencyContact(db.Model):
    """Emergency contacts of Saheli (e.g. parents, trusted friends)"""
    __tablename__ = 'emergency_contacts'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    priority_order = db.Column(db.Integer, default=1)
    notify_sms = db.Column(db.Boolean, default=True)
    notify_call = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='emergency_contacts')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'relationship': self.relationship,
            'priority_order': self.priority_order,
            'notify_sms': self.notify_sms,
            'notify_call': self.notify_call,
        }


class RefreshToken(db.Model):
    """Revocable JWT Refresh Token Store"""
    __tablename__ = 'refresh_tokens'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), nullable=True)
    guardian_id = db.Column(db.String(36), nullable=True)
    admin_id = db.Column(db.String(36), nullable=True)
    token_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
