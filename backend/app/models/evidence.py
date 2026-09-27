from datetime import datetime
from backend.app.database import db, generate_uuid

class CameraSnapshot(db.Model):
    """Still photo captured by ESP32-CAM during emergency or scheduled capture"""
    __tablename__ = 'camera_snapshots'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    incident_id = db.Column(db.String(36), db.ForeignKey('emergency_incidents.id', ondelete='SET NULL'), nullable=True, index=True)
    device_id = db.Column(db.String(64), db.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    storage_type = db.Column(db.String(20), default='LOCAL')  # 'LOCAL', 'S3', 'FIREBASE'
    file_size_bytes = db.Column(db.BigInteger, default=0)
    file_hash = db.Column(db.String(64), nullable=False)
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    captured_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('EmergencyIncident', back_populates='snapshots')
    device = db.relationship('Device', back_populates='snapshots')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'device_id': self.device_id,
            'image_url': self.image_url,
            'file_size_bytes': self.file_size_bytes,
            'file_hash': self.file_hash,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None,
            'captured_at': self.captured_at.isoformat() if self.captured_at else None,
        }


class CameraRecording(db.Model):
    """Short emergency video clip captured by ESP32-CAM"""
    __tablename__ = 'camera_recordings'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    incident_id = db.Column(db.String(36), db.ForeignKey('emergency_incidents.id', ondelete='SET NULL'), nullable=True, index=True)
    device_id = db.Column(db.String(64), db.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    storage_url = db.Column(db.String(500), nullable=False)
    storage_type = db.Column(db.String(20), default='LOCAL')
    duration_seconds = db.Column(db.Integer, default=0)
    file_size_bytes = db.Column(db.BigInteger, default=0)
    file_hash = db.Column(db.String(64), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('EmergencyIncident', back_populates='recordings')
    device = db.relationship('Device', back_populates='recordings')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'storage_url': self.storage_url,
            'duration_seconds': self.duration_seconds,
            'file_hash': self.file_hash,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }


class AudioRecording(db.Model):
    """Emergency audio clip captured by INMP441 microphone"""
    __tablename__ = 'audio_recordings'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    incident_id = db.Column(db.String(36), db.ForeignKey('emergency_incidents.id', ondelete='SET NULL'), nullable=True, index=True)
    device_id = db.Column(db.String(64), db.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    storage_url = db.Column(db.String(500), nullable=False)
    storage_type = db.Column(db.String(20), default='LOCAL')
    duration_seconds = db.Column(db.Integer, default=0)
    file_size_bytes = db.Column(db.BigInteger, default=0)
    file_hash = db.Column(db.String(64), nullable=False)
    trigger_type = db.Column(db.String(32), default='EMERGENCY')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('EmergencyIncident', back_populates='audio_records')
    device = db.relationship('Device', back_populates='audio_records')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'storage_url': self.storage_url,
            'duration_seconds': self.duration_seconds,
            'trigger_type': self.trigger_type,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }


class VoiceEvent(db.Model):
    """Keyword detection telemetry: 'HELP', 'SAVE ME', 'BACHAO'"""
    __tablename__ = 'voice_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(64), nullable=False, index=True)
    user_id = db.Column(db.String(36), nullable=True)
    keyword_detected = db.Column(db.String(64), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    audio_snippet_url = db.Column(db.String(500), nullable=True)
    triggered_incident_id = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class ClapEvent(db.Model):
    """Triple/double clap pattern telemetry"""
    __tablename__ = 'clap_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(64), nullable=False, index=True)
    user_id = db.Column(db.String(36), nullable=True)
    clap_count = db.Column(db.Integer, nullable=False)
    interval_pattern_ms = db.Column(db.String(128), nullable=True)
    confidence = db.Column(db.Float, nullable=False)
    triggered_incident_id = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class MovementEvent(db.Model):
    """MPU6050 Motion sensor anomaly: Fall, struggle, impact"""
    __tablename__ = 'movement_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(64), nullable=False, index=True)
    user_id = db.Column(db.String(36), nullable=True)
    accel_x = db.Column(db.Float, nullable=False)
    accel_y = db.Column(db.Float, nullable=False)
    accel_z = db.Column(db.Float, nullable=False)
    gyro_x = db.Column(db.Float, nullable=False)
    gyro_y = db.Column(db.Float, nullable=False)
    gyro_z = db.Column(db.Float, nullable=False)
    anomaly_type = db.Column(db.String(32), nullable=False, index=True)  # FALL, STRUGGLE, IMPACT
    confidence = db.Column(db.Float, nullable=False)
    triggered_incident_id = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
