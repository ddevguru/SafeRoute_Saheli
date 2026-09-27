from datetime import datetime
import bcrypt
from backend.app.database import db, generate_uuid

class Guardian(db.Model):
    """Guardian Account (Mother, Father, Spouse, Sibling, Trusted Mentor)"""
    __tablename__ = 'guardians'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(120), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(191), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    saheli_links = db.relationship('GuardianUser', back_populates='guardian', cascade='all, delete-orphan')
    device_tokens = db.relationship('DeviceToken', back_populates='guardian', cascade='all, delete-orphan')

    def set_password(self, plain_password: str) -> None:
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, plain_password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'relationship': self.relationship,
            'phone': self.phone,
            'email': self.email,
            'username': self.username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class GuardianUser(db.Model):
    """Many-to-Many Linking Table: Saheli <--> Guardian with permissions"""
    __tablename__ = 'guardian_users'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    saheli_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    guardian_id = db.Column(db.String(36), db.ForeignKey('guardians.id', ondelete='CASCADE'), nullable=False, index=True)
    relationship_label = db.Column(db.String(60), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    can_view_camera = db.Column(db.Boolean, default=False)
    can_view_location = db.Column(db.Boolean, default=True)
    emergency_override_camera = db.Column(db.Boolean, default=True)
    invitation_status = db.Column(db.String(20), default='ACCEPTED')  # PENDING, ACCEPTED, REVOKED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('saheli_id', 'guardian_id', name='uk_saheli_guardian'),
    )

    saheli = db.relationship('User', back_populates='guardian_links')
    guardian = db.relationship('Guardian', back_populates='saheli_links')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'saheli_id': self.saheli_id,
            'guardian_id': self.guardian_id,
            'relationship_label': self.relationship_label,
            'is_primary': self.is_primary,
            'can_view_camera': self.can_view_camera,
            'can_view_location': self.can_view_location,
            'emergency_override_camera': self.emergency_override_camera,
            'invitation_status': self.invitation_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
