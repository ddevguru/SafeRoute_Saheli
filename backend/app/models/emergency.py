from datetime import datetime, timedelta
import secrets
from backend.app.database import db, generate_uuid

class EmergencyIncident(db.Model):
    """Central Master Emergency Record"""
    __tablename__ = 'emergency_incidents'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    device_id = db.Column(db.String(64), nullable=True)
    trigger_type = db.Column(db.String(32), nullable=False)  # TOUCH, BUTTON, VOICE, CLAP, MOTION, MULTI_SIGNAL
    status = db.Column(db.String(20), default='ACTIVE', index=True)  # ACTIVE, CANCELLED, RESOLVED
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    accuracy_meters = db.Column(db.Float, default=5.0)
    battery_percent = db.Column(db.Integer, default=100)
    confidence = db.Column(db.Float, default=1.0)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    resolved_notes = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='incidents')
    notifications = db.relationship('EmergencyNotification', back_populates='incident', cascade='all, delete-orphan')
    tracking_sessions = db.relationship('LiveTrackingSession', back_populates='incident', cascade='all, delete-orphan')
    snapshots = db.relationship('CameraSnapshot', back_populates='incident')
    recordings = db.relationship('CameraRecording', back_populates='incident')
    audio_records = db.relationship('AudioRecording', back_populates='incident')
    location_points = db.relationship('LocationHistory', back_populates='incident')
    nearby_help_entries = db.relationship('NearbyHelpLog', back_populates='incident')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'device_id': self.device_id,
            'trigger_type': self.trigger_type,
            'status': self.status,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None,
            'accuracy_meters': self.accuracy_meters,
            'battery_percent': self.battery_percent,
            'confidence': self.confidence,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class EmergencyNotification(db.Model):
    """Notification dispatches associated with an active emergency"""
    __tablename__ = 'emergency_notifications'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    incident_id = db.Column(db.String(36), db.ForeignKey('emergency_incidents.id', ondelete='CASCADE'), nullable=False, index=True)
    recipient_type = db.Column(db.String(32), nullable=False)  # GUARDIAN, EMERGENCY_CONTACT, POLICE
    recipient_id = db.Column(db.String(36), nullable=True)
    recipient_phone = db.Column(db.String(20), nullable=True)
    channel = db.Column(db.String(20), nullable=False)  # FCM, SMS, CALL, SOCKET
    status = db.Column(db.String(20), default='PENDING')  # PENDING, SENT, DELIVERED, FAILED
    provider_reference = db.Column(db.String(128), nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('EmergencyIncident', back_populates='notifications')


class NotificationLog(db.Model):
    """Audit logging for all emergency SMS, Calls, and Push notifications"""
    __tablename__ = 'notification_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.String(36), nullable=True, index=True)
    channel = db.Column(db.String(32), nullable=False)
    destination = db.Column(db.String(191), nullable=False)
    payload = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), nullable=False)
    response_body = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class LiveTrackingSession(db.Model):
    """Secure web live tracking session without requiring Guardian app"""
    __tablename__ = 'live_tracking_sessions'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    incident_id = db.Column(db.String(36), db.ForeignKey('emergency_incidents.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tracking_token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('EmergencyIncident', back_populates='tracking_sessions')
    tokens = db.relationship('TrackingToken', back_populates='session', cascade='all, delete-orphan')

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(48)


class TrackingToken(db.Model):
    """Token validation and rate/access tracking for public emergency link"""
    __tablename__ = 'tracking_tokens'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    session_id = db.Column(db.String(36), db.ForeignKey('live_tracking_sessions.id', ondelete='CASCADE'), nullable=False)
    token_value = db.Column(db.String(128), unique=True, nullable=False, index=True)
    access_count = db.Column(db.Integer, default=0)
    last_accessed_at = db.Column(db.DateTime, nullable=True)
    is_revoked = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship('LiveTrackingSession', back_populates='tokens')
