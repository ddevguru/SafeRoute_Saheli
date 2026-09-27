import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from backend.app.database import db
from backend.app.models.device import DeviceToken
from backend.app.models.emergency import NotificationLog
from backend.app.auth.jwt_handler import jwt_required
from backend.app.notification.firebase_admin_client import FirebaseAdminClient

logger = logging.getLogger(__name__)

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')

@notification_bp.route('/tokens', methods=['POST'])
@jwt_required()
def register_device_token():
    """
    Register or update an FCM push notification token.
    Compatible with both Saheli (User) and Guardian tokens.
    """
    actor_id = g.user_id
    role = g.current_role
    data = request.get_json() or {}

    fcm_token = data.get('fcm_token', '').strip()
    platform = data.get('platform', 'ANDROID').upper()

    if not fcm_token:
        return jsonify({'success': False, 'error': 'fcm_token is required'}), 400

    if platform not in ('ANDROID', 'IOS', 'WEB'):
        platform = 'ANDROID'

    # Check if this token is already recorded
    token_record = DeviceToken.query.filter_by(fcm_token=fcm_token).first()
    if token_record:
        if role == 'GUARDIAN':
            token_record.guardian_id = actor_id
            token_record.user_id = None
        else:
            token_record.user_id = actor_id
            token_record.guardian_id = None

        token_record.platform = platform
        token_record.is_active = True
        token_record.updated_at = datetime.utcnow()
    else:
        token_record = DeviceToken(
            fcm_token=fcm_token,
            platform=platform,
            is_active=True,
            user_id=actor_id if role != 'GUARDIAN' else None,
            guardian_id=actor_id if role == 'GUARDIAN' else None
        )
        db.session.add(token_record)

    db.session.commit()
    logger.info(f"FCM token registered for {role} {actor_id} (Platform: {platform})")
    return jsonify({
        'success': True,
        'message': 'FCM token registered successfully',
        'token_id': token_record.id,
        'role': role
    }), 200


@notification_bp.route('/tokens', methods=['GET'])
@jwt_required()
def list_active_tokens():
    """Retrieve all active device tokens for the authenticated account"""
    actor_id = g.user_id
    role = g.current_role

    if role == 'GUARDIAN':
        tokens = DeviceToken.query.filter_by(guardian_id=actor_id, is_active=True).all()
    else:
        tokens = DeviceToken.query.filter_by(user_id=actor_id, is_active=True).all()

    result = [{
        'id': t.id,
        'fcm_token': t.fcm_token,
        'platform': t.platform,
        'created_at': t.created_at.isoformat() if t.created_at else None,
        'updated_at': t.updated_at.isoformat() if t.updated_at else None,
    } for t in tokens]

    return jsonify({'success': True, 'tokens': result, 'count': len(result)}), 200


@notification_bp.route('/tokens', methods=['DELETE'])
@jwt_required()
def revoke_device_token():
    """Deactivate device token on signout or device unpairing"""
    actor_id = g.user_id
    role = g.current_role
    data = request.get_json() or {}
    fcm_token = data.get('fcm_token', '').strip()

    query = DeviceToken.query
    if fcm_token:
        query = query.filter_by(fcm_token=fcm_token)
    else:
        if role == 'GUARDIAN':
            query = query.filter_by(guardian_id=actor_id)
        else:
            query = query.filter_by(user_id=actor_id)

    tokens = query.all()
    for t in tokens:
        t.is_active = False

    db.session.commit()
    return jsonify({'success': True, 'message': f'{len(tokens)} token(s) revoked successfully'}), 200


@notification_bp.route('/test', methods=['POST'])
@jwt_required()
def test_push_dispatch():
    """
    Send a test push notification to verified device tokens of current user.
    Useful for QA and device integration testing.
    """
    actor_id = g.user_id
    role = g.current_role
    data = request.get_json() or {}
    custom_title = data.get('title', '🧪 SafeRoute Saheli Test Alert')
    custom_body = data.get('body', 'Test notification received successfully from SafeRoute Saheli Cloud.')

    if role == 'GUARDIAN':
        tokens = DeviceToken.query.filter_by(guardian_id=actor_id, is_active=True).all()
    else:
        tokens = DeviceToken.query.filter_by(user_id=actor_id, is_active=True).all()

    if not tokens:
        return jsonify({
            'success': False,
            'error': 'No active FCM tokens registered for this account. Call POST /api/notifications/tokens first.'
        }), 404

    token_strings = [t.fcm_token for t in tokens]
    res = FirebaseAdminClient.send_multicast(
        tokens=token_strings,
        title=custom_title,
        body=custom_body,
        data={'type': 'TEST_NOTIFICATION', 'role': role, 'timestamp': datetime.utcnow().isoformat()},
        priority='high'
    )

    return jsonify({
        'success': True,
        'summary': res
    }), 200


@notification_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_notification_logs():
    """Retrieve audit history of notification dispatches"""
    limit = min(int(request.args.get('limit', 50)), 100)
    incident_id = request.args.get('incident_id')

    query = NotificationLog.query
    if incident_id:
        query = query.filter_by(incident_id=incident_id)

    logs = query.order_by(NotificationLog.created_at.desc()).limit(limit).all()
    results = [{
        'id': l.id,
        'incident_id': l.incident_id,
        'channel': l.channel,
        'destination': l.destination,
        'status': l.status,
        'payload': l.payload,
        'created_at': l.created_at.isoformat() if l.created_at else None
    } for l in logs]

    return jsonify({'success': True, 'logs': results, 'count': len(results)}), 200
