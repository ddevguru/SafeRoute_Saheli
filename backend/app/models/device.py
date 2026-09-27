from datetime import datetime
import hashlib
from backend.app.database import db, generate_uuid

class Device(db.Model):
    """Registered IoT Hardware: Wearable ESP32 or ESP32-CAM"""
    __tablename__ = 'devices'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    device_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    device_type = db.Column(db.String(32), nullable=False)  # 'ESP32_WEARABLE' or 'ESP32_CAM'
    device_secret_hash = db.Column(db.String(255), nullable=False)
    assigned_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    nickname = db.Column(db.String(80), nullable=True)
    is_paired = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='OFFLINE')  # 'ONLINE', 'OFFLINE', 'EMERGENCY'
    last_heartbeat = db.Column(db.DateTime, nullable=True)
    firmware_version = db.Column(db.String(32), default='1.0.0')
    battery_percent = db.Column(db.Integer, default=100)
    battery_voltage = db.Column(db.Float, default=4.20)
    wifi_rssi = db.Column(db.Integer, default=-60)
    camera_health = db.Column(db.String(50), default='IDLE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_user = db.relationship('User', back_populates='devices')
    snapshots = db.relationship('CameraSnapshot', back_populates='device')
    recordings = db.relationship('CameraRecording', back_populates='device')
    audio_records = db.relationship('AudioRecording', back_populates='device')

    def set_secret(self, secret: str) -> None:
        self.device_secret_hash = hashlib.sha256(secret.encode('utf-8')).hexdigest()

    def verify_secret(self, secret: str) -> bool:
        return self.device_secret_hash == hashlib.sha256(secret.encode('utf-8')).hexdigest()

    def to_dict(self) -> dict:
        # Physical device is only considered ONLINE if a heartbeat was received within the last 90 seconds
        is_live = False
        if self.last_heartbeat:
            delta_s = (datetime.utcnow() - self.last_heartbeat).total_seconds()
            if delta_s < 90:
                is_live = True

        calculated_status = 'ONLINE' if is_live else 'OFFLINE'
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_type': self.device_type,
            'assigned_user_id': self.assigned_user_id,
            'nickname': self.nickname,
            'is_paired': self.is_paired,
            'status': calculated_status,
            'is_online': is_live,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'firmware_version': self.firmware_version,
            'battery_percent': self.battery_percent if is_live else 0,
            'battery_voltage': self.battery_voltage if is_live else 0.0,
            'wifi_rssi': self.wifi_rssi if is_live else 0,
            'camera_health': self.camera_health if is_live else 'DISCONNECTED',
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class DeviceEvent(db.Model):
    """Raw IoT Telemetry Event Log"""
    __tablename__ = 'device_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(64), nullable=False, index=True)
    event_type = db.Column(db.String(64), nullable=False, index=True)
    event_payload = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class DeviceToken(db.Model):
    """FCM Push Notification Token for Mobile Apps"""
    __tablename__ = 'device_tokens'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    guardian_id = db.Column(db.String(36), db.ForeignKey('guardians.id', ondelete='CASCADE'), nullable=True, index=True)
    fcm_token = db.Column(db.String(500), unique=True, nullable=False)
    platform = db.Column(db.String(20), default='ANDROID')  # 'ANDROID', 'IOS', 'WEB'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='device_tokens')
    guardian = db.relationship('Guardian', back_populates='device_tokens')
