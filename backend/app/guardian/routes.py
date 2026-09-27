from datetime import datetime
from flask import Blueprint, request, jsonify, g
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.device import DeviceToken
from backend.app.models.emergency import EmergencyIncident
from backend.app.models.location import LocationHistory
from backend.app.models.admin import AuditLog
from backend.app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    roles_required
)

guardian_bp = Blueprint('guardian', __name__, url_prefix='/api/guardians')

@guardian_bp.route('', methods=['POST'])
@guardian_bp.route('/add', methods=['POST'])
@jwt_required()
@roles_required('SAHELI')
def add_guardian():
    """Saheli adds or links a Guardian account"""
    saheli_id = g.user_id
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    relationship = data.get('relationship', 'Guardian').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not name or not phone:
        return jsonify({'success': False, 'error': 'Name and phone are required'}), 400

    if not email:
        clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        email = f"{clean_phone}@saheli.guardian.safe"

    # Check if Guardian account already exists
    guardian = Guardian.query.filter((Guardian.email == email) | (Guardian.phone == phone)).first()
    if not guardian:
        if not username or not password:
            # Auto-generate temporary credentials if not provided
            username = email.split('@')[0] + "_g"
            password = "SafeSaheli@" + phone[-4:]

        guardian = Guardian(
            name=name,
            relationship=relationship,
            phone=phone,
            email=email,
            username=username
        )
        guardian.set_password(password)
        db.session.add(guardian)
        db.session.flush()

    # Link Guardian to Saheli
    existing_link = GuardianUser.query.filter_by(
        saheli_id=saheli_id,
        guardian_id=guardian.id
    ).first()

    if existing_link:
        return jsonify({'success': False, 'error': 'This guardian is already linked to your account'}), 409

    link = GuardianUser(
        saheli_id=saheli_id,
        guardian_id=guardian.id,
        relationship_label=relationship,
        is_primary=data.get('is_primary', False),
        can_view_camera=data.get('can_view_camera', False),
        can_view_location=data.get('can_view_location', True),
        emergency_override_camera=data.get('emergency_override_camera', True),
        invitation_status='ACCEPTED'
    )
    db.session.add(link)

    audit = AuditLog(
        actor_type='USER',
        actor_id=saheli_id,
        action='GUARDIAN_LINKED',
        resource='guardian_users',
        resource_id=guardian.id,
        details={'guardian_email': email, 'relationship': relationship}
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Guardian linked successfully',
        'guardian': guardian.to_dict(),
        'link': link.to_dict()
    }), 201


@guardian_bp.route('', methods=['GET'])
@jwt_required()
@roles_required('SAHELI')
def list_guardians():
    """List all guardians linked to current Saheli"""
    saheli_id = g.user_id
    links = GuardianUser.query.filter_by(saheli_id=saheli_id).all()
    results = []
    for link in links:
        guardian_dict = link.guardian.to_dict()
        guardian_dict['link_permissions'] = link.to_dict()
        results.append(guardian_dict)
    return jsonify({'success': True, 'guardians': results}), 200


@guardian_bp.route('/<string:guardian_id>', methods=['PUT'])
@jwt_required()
@roles_required('SAHELI')
def update_guardian_permissions(guardian_id):
    """Update permissions granted to a guardian"""
    saheli_id = g.user_id
    link = GuardianUser.query.filter_by(saheli_id=saheli_id, guardian_id=guardian_id).first()
    if not link:
        return jsonify({'success': False, 'error': 'Guardian link not found'}), 404

    data = request.get_json() or {}
    if 'can_view_camera' in data:
        link.can_view_camera = bool(data['can_view_camera'])
    if 'can_view_location' in data:
        link.can_view_location = bool(data['can_view_location'])
    if 'emergency_override_camera' in data:
        link.emergency_override_camera = bool(data['emergency_override_camera'])
    if 'is_primary' in data:
        link.is_primary = bool(data['is_primary'])

    db.session.commit()
    return jsonify({'success': True, 'message': 'Permissions updated', 'link': link.to_dict()}), 200


@guardian_bp.route('/<string:guardian_id>', methods=['DELETE'])
@jwt_required()
@roles_required('SAHELI')
def remove_guardian(guardian_id):
    """Unlink guardian from Saheli account"""
    saheli_id = g.user_id
    link = GuardianUser.query.filter_by(saheli_id=saheli_id, guardian_id=guardian_id).first()
    if not link:
        return jsonify({'success': False, 'error': 'Guardian link not found'}), 404

    db.session.delete(link)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Guardian unlinked'}), 200


@guardian_bp.route('/login', methods=['POST'])
def guardian_login():
    """Independent login for Guardian"""
    data = request.get_json() or {}
    identifier = data.get('username') or data.get('email') or data.get('phone')
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'success': False, 'error': 'Identifier and password are required'}), 400

    guardian = Guardian.query.filter(
        (Guardian.username == identifier) |
        (Guardian.email == identifier) |
        (Guardian.phone == identifier)
    ).first()

    if not guardian or not guardian.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid guardian credentials'}), 401

    if not guardian.is_active:
        return jsonify({'success': False, 'error': 'Account is inactive'}), 403

    access_token = create_access_token(guardian.id, role='GUARDIAN')
    refresh_token = create_refresh_token(guardian.id, role='GUARDIAN')

    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'guardian': guardian.to_dict()
    }), 200


@guardian_bp.route('/saheli-list', methods=['GET'])
@jwt_required()
@roles_required('GUARDIAN')
def get_monitored_sahelis():
    """List all Saheli accounts this guardian is authorized to monitor"""
    guardian_id = g.user_id
    links = GuardianUser.query.filter_by(guardian_id=guardian_id).all()
    results = []

    for link in links:
        saheli = link.saheli
        if not saheli or not saheli.is_active:
            continue
        active_incident = EmergencyIncident.query.filter_by(user_id=saheli.id, status='ACTIVE').first()
        latest_loc = LocationHistory.query.filter_by(user_id=saheli.id).order_by(LocationHistory.recorded_at.desc()).first()

        saheli_data = saheli.to_dict()
        saheli_data['permissions'] = {
            'can_view_camera': link.can_view_camera or (active_incident and link.emergency_override_camera),
            'can_view_location': link.can_view_location,
            'is_primary': link.is_primary,
            'relationship_label': link.relationship_label,
        }
        saheli_data['active_emergency'] = active_incident.to_dict() if active_incident else None
        saheli_data['latest_location'] = latest_loc.to_dict() if latest_loc else None
        saheli_data['safety_score'] = 82.0 if not active_incident else 15.0
        results.append(saheli_data)

    return jsonify({'success': True, 'sahelis': results}), 200


@guardian_bp.route('/device-token', methods=['POST'])
@jwt_required()
@roles_required('GUARDIAN')
def register_guardian_device_token():
    """Register Guardian FCM token for high-priority push notifications"""
    guardian_id = g.user_id
    data = request.get_json() or {}
    fcm_token = data.get('fcm_token', '').strip()
    platform = data.get('platform', 'ANDROID').upper()

    if not fcm_token:
        return jsonify({'success': False, 'error': 'fcm_token is required'}), 400

    existing = DeviceToken.query.filter_by(fcm_token=fcm_token).first()
    if existing:
        existing.guardian_id = guardian_id
        existing.is_active = True
    else:
        new_token = DeviceToken(
            guardian_id=guardian_id,
            fcm_token=fcm_token,
            platform=platform,
            is_active=True
        )
        db.session.add(new_token)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Guardian device token registered'}), 200
