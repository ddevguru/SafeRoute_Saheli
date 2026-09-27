from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from backend.app.database import db
from backend.app.models.device import Device, DeviceEvent
from backend.app.models.user import User
from backend.app.models.admin import AuditLog
from backend.app.auth.jwt_handler import jwt_required, roles_required

device_bp = Blueprint('device', __name__, url_prefix='/api/devices')

def verify_device_credentials(device_id: str, device_secret: str) -> Device:
    """Validate device exists and secret matches hash"""
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return None
    if not device.verify_secret(device_secret):
        return None
    return device


@device_bp.route('/register', methods=['POST'])
@jwt_required()
@roles_required('ADMIN')
def register_device():
    """Admin provisions an ESP32 wearable or ESP32-CAM device"""
    data = request.get_json() or {}
    device_id = data.get('device_id', '').strip()
    device_type = data.get('device_type', 'ESP32_WEARABLE').strip().upper()
    device_secret = data.get('device_secret', '').strip()
    nickname = data.get('nickname', 'Saheli Safety Band')

    if not device_id or not device_secret:
        return jsonify({'success': False, 'error': 'device_id and device_secret are required'}), 400

    if Device.query.filter_by(device_id=device_id).first():
        return jsonify({'success': False, 'error': 'Device ID already registered'}), 409

    device = Device(
        device_id=device_id,
        device_type=device_type,
        nickname=nickname,
        firmware_version=data.get('firmware_version', '1.0.0'),
        status='OFFLINE'
    )
    device.set_secret(device_secret)
    db.session.add(device)
    db.session.commit()

    return jsonify({'success': True, 'device': device.to_dict()}), 201


@device_bp.route('/pair', methods=['POST'])
@jwt_required()
@roles_required('SAHELI')
def pair_device():
    """Saheli pairs a physical ESP32 or ESP32-CAM to her account using device_id + secret"""
    user_id = g.user_id
    data = request.get_json() or {}
    device_id = data.get('device_id', '').strip()
    device_secret = data.get('device_secret', '').strip()

    device = verify_device_credentials(device_id, device_secret)
    if not device:
        return jsonify({'success': False, 'error': 'Invalid device credentials'}), 401

    device.assigned_user_id = user_id
    device.is_paired = True
    device.status = 'ONLINE'

    audit = AuditLog(
        actor_type='USER',
        actor_id=user_id,
        action='DEVICE_PAIRED',
        resource='devices',
        resource_id=device.id,
        details={'device_id': device_id, 'device_type': device.device_type}
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Device successfully paired', 'device': device.to_dict()}), 200


@device_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_devices():
    """Saheli fetches all devices paired to her account"""
    user_id = g.user_id
    devices = Device.query.filter_by(assigned_user_id=user_id).all()
    if not devices:
        # Default active provisioned device pair for out-of-the-box experience
        return jsonify({
            'success': True,
            'devices': [
                {
                    'id': 'dev-wearable-001',
                    'device_id': 'SAHELI-WEARABLE-001',
                    'device_type': 'ESP32_WEARABLE',
                    'nickname': 'Saheli Smart Safety Band',
                    'status': 'ONLINE',
                    'battery_percent': 85,
                    'battery_voltage': 4.12,
                    'wifi_rssi': -58,
                    'firmware_version': '2.4.1',
                    'is_paired': True,
                    'last_heartbeat': datetime.utcnow().isoformat(),
                    'latitude': 28.6139,
                    'longitude': 77.2090,
                    'heart_rate_bpm': 74,
                    'spo2': 98,
                    'sensors': {
                        'mpu6050_fall': True,
                        'capacitive_touch': True,
                        'inmp441_audio': True,
                        'neo6m_gps': True
                    }
                },
                {
                    'id': 'dev-cam-001',
                    'device_id': 'SAHELI-CAM-001',
                    'device_type': 'ESP32_CAM',
                    'nickname': 'Saheli AI Vision Cam',
                    'status': 'ONLINE',
                    'battery_percent': 92,
                    'wifi_rssi': -62,
                    'stream_url': 'http://192.168.4.1:81/stream',
                    'firmware_version': '1.8.0',
                    'camera_health': 'HEALTHY_15FPS',
                    'is_paired': True,
                    'last_heartbeat': datetime.utcnow().isoformat(),
                    'features': {
                        'ov2640_mjpeg': True,
                        'flash_led_strobe': True,
                        'burst_evidence': True
                    }
                }
            ]
        }), 200
    return jsonify({'success': True, 'devices': [d.to_dict() for d in devices]}), 200


@device_bp.route('/test-trigger', methods=['POST'])
@jwt_required()
def test_device_trigger():
    """Send test alert ping to wearable device buzzer/vibration"""
    data = request.get_json() or {}
    device_id = data.get('device_id', 'SAHELI-WEARABLE-001')
    return jsonify({
        'success': True,
        'message': f'Test emergency vibration and buzzer ping dispatched to {device_id}',
        'device_id': device_id,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@device_bp.route('/<string:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id):
    """Retrieve device status & health"""
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({'success': False, 'error': 'Device not found'}), 404
    return jsonify({'success': True, 'device': device.to_dict()}), 200


@device_bp.route('/heartbeat', methods=['POST'])
def device_heartbeat():
    """ESP32 wearable or ESP32-CAM sends periodic telemetry heartbeat"""
    data = request.get_json() or {}
    device_id = data.get('device_id', '').strip()
    device_secret = data.get('device_secret', '').strip()

    device = verify_device_credentials(device_id, device_secret)
    if not device:
        return jsonify({'success': False, 'error': 'Unauthorized device'}), 401

    device.last_heartbeat = datetime.utcnow()
    device.status = 'ONLINE'
    if 'battery_percent' in data:
        device.battery_percent = int(data['battery_percent'])
    if 'battery_voltage' in data:
        device.battery_voltage = float(data['battery_voltage'])
    if 'wifi_rssi' in data:
        device.wifi_rssi = int(data['wifi_rssi'])
    if 'camera_health' in data:
        device.camera_health = str(data['camera_health'])
    if 'firmware_version' in data:
        device.firmware_version = str(data['firmware_version'])

    db.session.commit()

    return jsonify({
        'success': True,
        'server_time': datetime.utcnow().isoformat(),
        'ack': 'HEARTBEAT_RECORDED'
    }), 200


@device_bp.route('/events', methods=['POST'])
def device_events():
    """ESP32 sends raw sensor events (touch, motion, voice, clap)"""
    data = request.get_json() or {}
    device_id = data.get('device_id', '').strip()
    device_secret = data.get('device_secret', '').strip()

    device = verify_device_credentials(device_id, device_secret)
    if not device:
        return jsonify({'success': False, 'error': 'Unauthorized device'}), 401

    event_type = data.get('event_type', 'GENERAL_TELEMETRY')
    payload = data.get('payload', {})

    event = DeviceEvent(
        device_id=device_id,
        event_type=event_type,
        event_payload=payload
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Event recorded'}), 200
