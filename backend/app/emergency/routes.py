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


@emergency_bp.route('/sms-webhook', methods=['POST'])
def sms_emergency_webhook():
    """
    Offline GSM / Cellular SMS Emergency Trigger Ingestion Webhook:
    Enables instant SOS triggering in areas with ZERO INTERNET connectivity via cellular SMS.
    Payload formats supported:
    1. Form-encoded (Twilio / Exotel / GSM Modem gateway) with 'From' and 'Body'
    2. JSON payload {'from': '+91...', 'body': 'SR_SOS|phone|lat|lng|trigger|battery'}
    """
    from backend.app.models.user import User

    sender = request.form.get('From') or request.json.get('from', '') if request.is_json else request.form.get('From', '')
    body = request.form.get('Body') or request.json.get('body', '') if request.is_json else request.form.get('Body', '')

    sender = str(sender).strip()
    body = str(body).strip()

    if not body:
        return jsonify({'success': False, 'error': 'Empty SMS body'}), 400

    # Parse compact protocol: SR_SOS|<phone>|<lat>|<lng>|<trigger>|<battery>
    phone = sender
    lat, lng = 28.6139, 77.2090
    trigger_type = 'SMS_OFFLINE'
    battery = 100

    if body.startswith('SR_SOS|') or '|' in body:
        parts = body.split('|')
        if len(parts) >= 2 and parts[1]:
            phone = parts[1].strip()
        if len(parts) >= 4:
            try:
                lat = float(parts[2])
                lng = float(parts[3])
            except ValueError:
                pass
        if len(parts) >= 5 and parts[4]:
            trigger_type = f"SMS_{parts[4].upper()}"
        if len(parts) >= 6:
            try:
                battery = int(parts[5].replace('%', ''))
            except ValueError:
                pass

    # Normalize phone: remove non-digit characters except leading +
    cleaned_phone = ''.join([c for c in phone if c.isdigit() or c == '+'])
    user = User.query.filter((User.phone == cleaned_phone) | (User.phone.endswith(cleaned_phone[-10:]))).first()

    if not user:
        return jsonify({
            'success': False,
            'error': f"No Saheli account found matching telephone {phone}"
        }), 404

    socketio = current_app.extensions.get('socketio')
    result = EmergencyService.trigger_emergency(
        user_id=user.id,
        trigger_type=trigger_type,
        latitude=lat,
        longitude=lng,
        device_id="GSM-SIM800L-OFFLINE",
        confidence=1.0,
        battery_percent=battery,
        socketio=socketio
    )

    # Return Twilio TwiML compatible XML or JSON response
    tracking_url = result.get('tracking_url', '')
    reply_sms = f"SAFEROUTE SAHELI ALERT ACKNOWLEDGED! Help is dispatched. Live tracking: {tracking_url}"

    if 'text/xml' in request.headers.get('Accept', '') or 'From' in request.form:
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply_sms}</Message></Response>'
        return twiml, 200, {'Content-Type': 'application/xml'}

    result['reply_sms'] = reply_sms
    return jsonify(result), 200


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


@emergency_bp.route('/biometric-telemetry', methods=['POST'])
@jwt_required(optional=True)
def receive_biometric_telemetry():
    """
    Ingest PPG biometric telemetry (Heart Rate BPM, SpO2, HRV, Accelerometer motion)
    from ESP32 MAX30102 wearable or mobile companion.
    Evaluates acute tachycardia panic spikes and auto-triggers emergency if panic is verified.
    """
    from ai_ml.models.biometric_stress_detector import get_biometric_detector

    data = request.get_json() or {}
    user_id = getattr(g, 'user_id', None)
    device_id = data.get('device_id')
    device_secret = data.get('device_secret')

    if not user_id and device_id and device_secret:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device or not device.verify_secret(device_secret):
            return jsonify({'success': False, 'error': 'Invalid device authentication'}), 401
        if not device.assigned_user_id:
            return jsonify({'success': False, 'error': 'Device is not paired to any Saheli account'}), 400
        user_id = device.assigned_user_id

    if not user_id:
        return jsonify({'success': False, 'error': 'User identification is required'}), 401

    bpm = float(data.get('heart_rate_bpm', 0.0))
    spo2 = float(data.get('spo2', 0.0))
    accel_mag = float(data.get('accel_mag_g', 1.0))
    rr_intervals = data.get('rr_intervals_ms')
    is_finger = bool(data.get('is_finger_detected', True))
    user_baseline = float(data.get('baseline_bpm', 75.0)) if data.get('baseline_bpm') else None

    detector = get_biometric_detector()
    assessment = detector.evaluate_biometrics(
        bpm=bpm,
        spo2=spo2,
        accel_mag_g=accel_mag,
        user_baseline_bpm=user_baseline,
        rr_intervals_ms=rr_intervals,
        is_finger_detected=is_finger
    )

    incident_result = None
    if assessment['is_emergency']:
        latitude = float(data.get('latitude', 28.6139))
        longitude = float(data.get('longitude', 77.2090))
        battery_percent = int(data.get('battery_percent', 100))
        trigger_type = 'BIOMETRIC_HYPOXIA' if assessment.get('is_hypoxia_emergency') else 'BIOMETRIC_PANIC'

        socketio = current_app.extensions.get('socketio')
        incident_result = EmergencyService.trigger_emergency(
            user_id=user_id,
            trigger_type=trigger_type,
            latitude=latitude,
            longitude=longitude,
            device_id=device_id,
            confidence=assessment['confidence'],
            battery_percent=battery_percent,
            socketio=socketio
        )

    return jsonify({
        'success': True,
        'assessment': assessment,
        'emergency_triggered': assessment['is_emergency'],
        'incident': incident_result
    }), 200
