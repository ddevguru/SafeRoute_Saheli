"""
SafeRoute Saheli — Geo-Fence Safe Zones & Battery Optimizer REST API (Phase 30)
Provides endpoints for CRUD management of user-defined safe zones and real-time evaluation.
"""

from flask import Blueprint, request, jsonify, g
from backend.app.database import db
from backend.app.models.routing import SafeZone
from backend.app.auth.jwt_handler import jwt_required
from backend.app.services.geofence_service import GeoFenceService

geofence_bp = Blueprint('geofence', __name__, url_prefix='/api/geofence')


@geofence_bp.route('/safe-zones', methods=['POST'])
@jwt_required()
def create_safe_zone():
    """Create a user-defined safe zone (Home, College, Office, Hostel)"""
    user_id = g.user_id
    data = request.get_json() or {}

    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'error': 'Safe zone name is required'}), 400

    try:
        lat = float(data.get('latitude', 0.0))
        lng = float(data.get('longitude', 0.0))
        radius = float(data.get('radius_meters', 150.0))
        curfew_start = int(data['curfew_start_hour']) if data.get('curfew_start_hour') is not None else None
        curfew_end = int(data['curfew_end_hour']) if data.get('curfew_end_hour') is not None else None
    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': f'Invalid coordinate or parameter format: {str(e)}'}), 400

    zone = SafeZone(
        user_id=user_id,
        name=name,
        latitude=lat,
        longitude=lng,
        radius_meters=radius,
        curfew_start_hour=curfew_start,
        curfew_end_hour=curfew_end,
        notify_guardians_on_arrival=bool(data.get('notify_guardians_on_arrival', True)),
        notify_guardians_on_departure=bool(data.get('notify_guardians_on_departure', False)),
        is_active=True
    )
    db.session.add(zone)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Safe zone "{name}" created successfully',
        'safe_zone': zone.to_dict()
    }), 201


@geofence_bp.route('/safe-zones', methods=['GET'])
@jwt_required()
def get_safe_zones():
    """Retrieve all safe zones for current user"""
    user_id = g.user_id
    zones = SafeZone.query.filter_by(user_id=user_id, is_active=True).order_by(SafeZone.created_at.desc()).all()
    return jsonify({
        'success': True,
        'count': len(zones),
        'safe_zones': [z.to_dict() for z in zones]
    }), 200


@geofence_bp.route('/evaluate', methods=['POST'])
@jwt_required()
def evaluate_geofence():
    """
    Real-time position evaluation against registered safe zones:
    Returns safe zone presence, battery-saving throttled GPS interval, and curfew alerts.
    """
    user_id = g.user_id
    data = request.get_json() or {}

    try:
        lat = float(data.get('latitude', 0.0))
        lng = float(data.get('longitude', 0.0))
        battery = int(data.get('battery_percent', 100))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid latitude, longitude, or battery level'}), 400

    result = GeoFenceService.evaluate_position(
        user_id=user_id,
        latitude=lat,
        longitude=lng,
        battery_percent=battery
    )

    return jsonify({
        'success': True,
        'evaluation': result
    }), 200


@geofence_bp.route('/safe-zones/<string:zone_id>', methods=['DELETE'])
@jwt_required()
def delete_safe_zone(zone_id):
    """Delete a user-defined safe zone"""
    user_id = g.user_id
    zone = SafeZone.query.filter_by(id=zone_id, user_id=user_id).first()
    if not zone:
        return jsonify({'success': False, 'error': 'Safe zone not found or unauthorized'}), 404

    db.session.delete(zone)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Safe zone deleted successfully'}), 200
