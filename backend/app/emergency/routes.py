from flask import Blueprint, request, jsonify, g, current_app
from backend.app.database import db
from backend.app.models.emergency import EmergencyIncident
from backend.app.models.device import Device
from backend.app.auth.jwt_handler import jwt_required
from backend.app.services.emergency_service import EmergencyService

emergency_bp = Blueprint('emergency', __name__, url_prefix='/api/emergency')

@emergency_bp.route('/trigger', methods=['POST'])
@jwt_required(optional=True)
def trigger():
    """
    Trigger Emergency:
    Can be called by:
    1. Authenticated Saheli Mobile App (JWT user_id)
    2. ESP32 Wearable Device (with device_id + device_secret in payload)
    """
    data = request.get_json() or {}
    user_id = getattr(g, 'user_id', None)
    device_id = data.get('device_id')
    device_secret = data.get('device_secret')

    # If triggered by IoT Hardware without User JWT
    if not user_id and device_id and device_secret:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device or not device.verify_secret(device_secret):
            return jsonify({'success': False, 'error': 'Invalid device authentication'}), 401
        if not device.assigned_user_id:
            return jsonify({'success': False, 'error': 'Device is not paired to any Saheli account'}), 400
        user_id = device.assigned_user_id

    if not user_id:
        return jsonify({'success': False, 'error': 'User identification is required'}), 401

    trigger_type = data.get('trigger_type', 'BUTTON').upper()  # TOUCH, BUTTON, VOICE, CLAP, MOTION
    latitude = float(data.get('latitude', 28.6139))
    longitude = float(data.get('longitude', 77.2090))
    battery_percent = int(data.get('battery_percent', 100))
    confidence = float(data.get('confidence', 1.0))

    socketio = current_app.extensions.get('socketio')

    try:
        result = EmergencyService.trigger_emergency(
            user_id=user_id,
            trigger_type=trigger_type,
            latitude=latitude,
            longitude=longitude,
            device_id=device_id,
            confidence=confidence,
            battery_percent=battery_percent,
            socketio=socketio
        )
        return jsonify(result), 200
    except Exception as ex:
        return jsonify({'success': False, 'error': str(ex)}), 500


@emergency_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_emergency():
    """Fetch active emergency for current user or monitored Saheli"""
    user_id = g.user_id
    role = g.current_role

    if role == 'SAHELI':
        incident = EmergencyIncident.query.filter_by(user_id=user_id, status='ACTIVE').first()
    elif role == 'GUARDIAN':
        from backend.app.models.guardian import GuardianUser
        links = GuardianUser.query.filter_by(guardian_id=user_id).all()
        saheli_ids = [l.saheli_id for l in links]
        incident = EmergencyIncident.query.filter(
            EmergencyIncident.user_id.in_(saheli_ids),
            EmergencyIncident.status == 'ACTIVE'
        ).first()
    else:
        # Admin or operator
        incident = EmergencyIncident.query.filter_by(status='ACTIVE').order_by(EmergencyIncident.started_at.desc()).first()

    if not incident:
        return jsonify({'success': True, 'active': False, 'incident': None}), 200

    return jsonify({'success': True, 'active': True, 'incident': incident.to_dict()}), 200


@emergency_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Retrieve emergency history with evidence links"""
    user_id = g.user_id
    incidents = EmergencyIncident.query.filter_by(user_id=user_id).order_by(EmergencyIncident.started_at.desc()).limit(50).all()
    results = [inc.to_dict() for inc in incidents]
    return jsonify({'success': True, 'incidents': results}), 200


@emergency_bp.route('/<string:incident_id>/cancel', methods=['POST'])
@jwt_required()
def cancel(incident_id):
    """Cancel emergency with press-and-hold confirmation"""
    user_id = g.user_id
    data = request.get_json() or {}
    reason = data.get('reason', 'User verified false alarm or safe condition')

    socketio = current_app.extensions.get('socketio')
    result = EmergencyService.cancel_emergency(incident_id, user_id=user_id, reason=reason, socketio=socketio)
    return jsonify(result), (200 if result['success'] else 400)


@emergency_bp.route('/<string:incident_id>/resolve', methods=['POST'])
@jwt_required()
def resolve(incident_id):
    """Mark emergency as resolved with closing notes"""
    resolver_id = g.user_id
    resolver_role = g.current_role
    data = request.get_json() or {}
    notes = data.get('notes', 'Incident resolved safely')

    socketio = current_app.extensions.get('socketio')
    result = EmergencyService.resolve_emergency(incident_id, resolver_id=resolver_id, resolver_role=resolver_role, notes=notes, socketio=socketio)
    return jsonify(result), (200 if result['success'] else 400)
