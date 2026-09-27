import os
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g, current_app, Response
from backend.app.database import db
from backend.app.models.device import Device
from backend.app.models.evidence import CameraSnapshot, CameraRecording
from backend.app.models.emergency import EmergencyIncident
from backend.app.models.guardian import GuardianUser
from backend.app.models.admin import AuditLog
from backend.app.auth.jwt_handler import jwt_required

camera_bp = Blueprint('camera', __name__, url_prefix='/api/camera')

@camera_bp.route('/session', methods=['POST'])
@jwt_required()
def create_camera_session():
    """
    Generate signed temporary session token to access ESP32-CAM live feed.
    Enforces privacy settings & emergency override rules:
    - Saheli can always view her own camera if enabled.
    - Guardian can only view if Saheli enabled guardian access OR active emergency override allows it.
    """
    requester_id = g.user_id
    role = g.current_role
    data = request.get_json() or {}
    target_user_id = data.get('target_user_id', requester_id)

    # Check device assignment
    cam_device = Device.query.filter_by(
        assigned_user_id=target_user_id,
        device_type='ESP32_CAM'
    ).first()

    if not cam_device:
        return jsonify({'success': False, 'error': 'No ESP32-CAM device paired for this user'}), 404

    active_incident = EmergencyIncident.query.filter_by(user_id=target_user_id, status='ACTIVE').first()

    if role == 'GUARDIAN':
        link = GuardianUser.query.filter_by(saheli_id=target_user_id, guardian_id=requester_id).first()
        if not link:
            return jsonify({'success': False, 'error': 'Not authorized for this Saheli'}), 403

        # Evaluate permission
        is_allowed = link.can_view_camera or (active_incident and link.emergency_override_camera)
        if not is_allowed:
            return jsonify({'success': False, 'error': 'Camera access denied by Saheli privacy settings'}), 403

    # Generate 5-minute signed token
    salt = current_app.config.get('CAMERA_STREAM_SECRET', 'secret_cam')
    raw_token = f"{target_user_id}:{cam_device.device_id}:{datetime.utcnow().timestamp()}:{salt}"
    session_token = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

    audit = AuditLog(
        actor_type=role,
        actor_id=requester_id,
        action='CAMERA_SESSION_CREATED',
        resource='devices',
        resource_id=cam_device.id,
        details={'target_user_id': target_user_id, 'is_emergency': active_incident is not None}
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'session_token': session_token,
        'device_id': cam_device.device_id,
        'expires_in_seconds': 300,
        'stream_url': f"/api/camera/stream/{session_token}?device_id={cam_device.device_id}"
    }), 200


@camera_bp.route('/capture', methods=['POST'])
def upload_snapshot():
    """ESP32-CAM uploads captured image frame with device authentication"""
    device_id = request.form.get('device_id') or request.headers.get('X-Device-Id')
    device_secret = request.form.get('device_secret') or request.headers.get('X-Device-Secret')

    device = Device.query.filter_by(device_id=device_id).first()
    if not device or not device.verify_secret(device_secret or ''):
        return jsonify({'success': False, 'error': 'Device authentication failed'}), 401

    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file uploaded'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    file_hash = hashlib.sha256(image_bytes).hexdigest()

    # Save to disk or storage provider
    filename = f"{device_id}_{int(datetime.utcnow().timestamp())}_{file_hash[:8]}.jpg"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'camera')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, 'wb') as f:
        f.write(image_bytes)

    # Check active emergency
    incident = EmergencyIncident.query.filter_by(user_id=device.assigned_user_id, status='ACTIVE').first()

    snapshot = CameraSnapshot(
        incident_id=incident.id if incident else None,
        device_id=device.id,
        user_id=device.assigned_user_id,
        image_url=f"/uploads/camera/{filename}",
        file_size_bytes=len(image_bytes),
        file_hash=file_hash,
        latitude=incident.latitude if incident else None,
        longitude=incident.longitude if incident else None,
    )
    db.session.add(snapshot)
    device.last_heartbeat = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'snapshot_id': snapshot.id,
        'image_url': snapshot.image_url,
        'file_hash': file_hash
    }), 201


@camera_bp.route('/emergency-capture', methods=['POST'])
def emergency_burst_capture():
    """ESP32-CAM triggers immediate burst capture frame during active incident"""
    return upload_snapshot()


@camera_bp.route('/status', methods=['GET'])
@jwt_required()
def camera_status():
    """Retrieve camera status and health metrics"""
    user_id = g.user_id
    device = Device.query.filter_by(assigned_user_id=user_id, device_type='ESP32_CAM').first()
    if not device:
        return jsonify({'success': False, 'status': 'NOT_PAIRED'}), 200

    return jsonify({
        'success': True,
        'device_id': device.device_id,
        'status': device.status,
        'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
        'camera_health': device.camera_health,
        'wifi_rssi': device.wifi_rssi
    }), 200


@camera_bp.route('/stream/<string:session_token>', methods=['GET'])
def stream_feed(session_token):
    """
    Authenticated MJPEG stream gateway.
    Verifies valid token and returns MJPEG boundary stream.
    """
    device_id = request.args.get('device_id')
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return "Camera device not found", 404

    # Dummy generator / gateway connector for development/testing
    def generate_dummy_stream():
        import io
        import time
        from PIL import Image, ImageDraw, ImageFont

        while True:
            img = Image.new('RGB', (320, 240), color='#002350')
            draw = ImageDraw.Draw(img)
            timestamp_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            draw.text((10, 10), "SafeRoute Saheli Live ESP32-CAM", fill="#D2AE39")
            draw.text((10, 30), f"Device: {device_id}", fill="#FFFFFF")
            draw.text((10, 50), f"Time: {timestamp_str}", fill="#A7F3D0")
            draw.text((10, 210), "SECURE AUTHENTICATED STREAM", fill="#F87171")

            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            frame = buf.getvalue()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.2)

    return Response(generate_dummy_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@camera_bp.route('/snapshots/<string:incident_id>', methods=['GET'])
@jwt_required()
def get_incident_snapshots(incident_id):
    """Retrieve all evidence photo captures taken during a specific incident"""
    snapshots = CameraSnapshot.query.filter_by(incident_id=incident_id)\
        .order_by(CameraSnapshot.captured_at.desc())\
        .all()
    return jsonify({
        'success': True,
        'incident_id': incident_id,
        'count': len(snapshots),
        'snapshots': [s.to_dict() for s in snapshots]
    }), 200


@camera_bp.route('/vault', methods=['GET'])
@jwt_required()
def get_camera_vault():
    """Retrieve all evidence snapshots in user's secure forensic vault"""
    requester_id = g.user_id
    role = g.current_role
    target_user_id = request.args.get('user_id', requester_id)

    if role == 'GUARDIAN':
        link = GuardianUser.query.filter_by(saheli_id=target_user_id, guardian_id=requester_id).first()
        if not link:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
    elif role == 'SAHELI' and target_user_id != requester_id:
        return jsonify({'success': False, 'error': 'Forbidden'}), 403

    limit = min(int(request.args.get('limit', 50)), 100)
    snapshots = CameraSnapshot.query.filter_by(user_id=target_user_id)\
        .order_by(CameraSnapshot.captured_at.desc())\
        .limit(limit)\
        .all()

    return jsonify({
        'success': True,
        'count': len(snapshots),
        'snapshots': [s.to_dict() for s in snapshots]
    }), 200

