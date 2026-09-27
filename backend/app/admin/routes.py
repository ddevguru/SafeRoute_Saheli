from flask import Blueprint, request, jsonify, g
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import Guardian
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident
from backend.app.models.evidence import CameraSnapshot, AudioRecording
from backend.app.models.routing import SafePlace, RiskFeature
from backend.app.models.admin import AdminUser, AuditLog
from backend.app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    roles_required
)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin and safety operator authentication"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    admin = AdminUser.query.filter((AdminUser.username == username) | (AdminUser.email == username)).first()
    if not admin or not admin.check_password(password):
        # Demo fallback for initial setup if admin not yet seeded in local DB
        if username == 'admin' and password == 'SaheliAdmin@2026':
            access_token = create_access_token('adm-001', role='ADMIN', extra_claims={'username': 'admin'})
            return jsonify({
                'success': True,
                'access_token': access_token,
                'role': 'SUPERADMIN',
                'username': 'admin'
            }), 200
        return jsonify({'success': False, 'error': 'Invalid administrator credentials'}), 401

    access_token = create_access_token(admin.id, role='ADMIN', extra_claims={'username': admin.username})
    refresh_token = create_refresh_token(admin.id, role='ADMIN')

    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'admin': admin.to_dict()
    }), 200


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def dashboard_metrics():
    """Central administrative statistics for SafeRoute Saheli Command Center"""
    total_users = User.query.count()
    total_guardians = Guardian.query.count()
    total_devices = Device.query.count()
    active_devices = Device.query.filter_by(status='ONLINE').count()
    active_emergencies = EmergencyIncident.query.filter_by(status='ACTIVE').count()
    total_incidents = EmergencyIncident.query.count()
    total_safe_places = SafePlace.query.count()

    return jsonify({
        'success': True,
        'metrics': {
            'total_users': total_users,
            'total_guardians': total_guardians,
            'total_devices': total_devices,
            'active_devices': active_devices,
            'active_emergencies': active_emergencies,
            'total_incidents': total_incidents,
            'total_safe_places': total_safe_places,
        }
    }), 200


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_users():
    """List all registered Saheli users"""
    users = User.query.order_by(User.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'users': [u.to_dict() for u in users]}), 200


@admin_bp.route('/devices', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_devices():
    """List all hardware wearable devices & ESP32-CAMs"""
    devices = Device.query.all()
    return jsonify({'success': True, 'devices': [d.to_dict() for d in devices]}), 200


@admin_bp.route('/emergencies', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_emergencies():
    """List emergency incidents with optional status filter"""
    status_filter = request.args.get('status')
    query = EmergencyIncident.query
    if status_filter:
        query = query.filter_by(status=status_filter.upper())
    incidents = query.order_by(EmergencyIncident.started_at.desc()).limit(100).all()
    return jsonify({'success': True, 'emergencies': [i.to_dict() for i in incidents]}), 200


@admin_bp.route('/cameras', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_cameras():
    """List ESP32-CAM camera statuses and snapshots"""
    cameras = Device.query.filter_by(device_type='ESP32_CAM').all()
    snapshots = CameraSnapshot.query.order_by(CameraSnapshot.captured_at.desc()).limit(20).all()
    return jsonify({
        'success': True,
        'cameras': [c.to_dict() for c in cameras],
        'recent_snapshots': [s.to_dict() for s in snapshots]
    }), 200


@admin_bp.route('/audio', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_audio_evidence():
    """List audio evidence recordings"""
    records = AudioRecording.query.order_by(AudioRecording.recorded_at.desc()).limit(50).all()
    return jsonify({'success': True, 'recordings': [r.to_dict() for r in records]}), 200


@admin_bp.route('/high-risk-zones', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_high_risk_zones():
    """List spatial benchmark high risk zones"""
    zones = RiskFeature.query.filter(RiskFeature.crime_rate > 0.4).all()
    results = [{
        'id': z.id,
        'latitude': float(z.latitude),
        'longitude': float(z.longitude),
        'radius_meters': z.radius_meters,
        'crime_rate': z.crime_rate,
        'lighting_quality': z.lighting_quality,
        'isolation_index': z.isolation_index
    } for z in zones]
    return jsonify({'success': True, 'zones': results}), 200


@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_audit_logs():
    """View security & privacy audit trail"""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'audit_logs': [l.to_dict() for l in logs]}), 200
