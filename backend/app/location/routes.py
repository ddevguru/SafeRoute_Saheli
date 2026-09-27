from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app, render_template_string
from backend.app.database import db
from backend.app.models.location import LocationHistory
from backend.app.models.emergency import EmergencyIncident, LiveTrackingSession, TrackingToken
from backend.app.models.user import User
from backend.app.models.guardian import GuardianUser
from backend.app.auth.jwt_handler import jwt_required

location_bp = Blueprint('location', __name__)

@location_bp.route('/api/location/update', methods=['POST'])
@jwt_required(optional=True)
def update_location():
    """Update user GPS coordinates (from Flutter mobile or ESP32 hardware)"""
    data = request.get_json() or {}
    user_id = getattr(g, 'user_id', None)
    device_id = data.get('device_id')
    device_secret = data.get('device_secret')

    if not user_id and device_id and device_secret:
        from backend.app.models.device import Device
        device = Device.query.filter_by(device_id=device_id).first()
        if device and device.verify_secret(device_secret):
            user_id = device.assigned_user_id

    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized location update'}), 401

    lat = float(data.get('latitude', 0.0))
    lng = float(data.get('longitude', 0.0))
    accuracy = float(data.get('accuracy', 5.0))
    speed = float(data.get('speed', 0.0))
    heading = float(data.get('heading', 0.0))
    battery = int(data.get('battery', 100))

    # Check if there is an active emergency
    active_incident = EmergencyIncident.query.filter_by(user_id=user_id, status='ACTIVE').first()
    is_emergency = active_incident is not None

    loc = LocationHistory(
        user_id=user_id,
        device_id=device_id,
        incident_id=active_incident.id if active_incident else None,
        latitude=lat,
        longitude=lng,
        accuracy=accuracy,
        speed=speed,
        heading=heading,
        is_emergency=is_emergency,
        battery_level=battery
    )
    db.session.add(loc)

    # If in active emergency, update incident position
    if active_incident:
        active_incident.latitude = lat
        active_incident.longitude = lng
        active_incident.battery_percent = battery

    db.session.commit()

    # Emit real-time WebSocket update to Saheli room & Admin
    socketio = current_app.extensions.get('socketio')
    if socketio:
        payload = loc.to_dict()
        socketio.emit('location_updated', payload, room=f"saheli_{user_id}")
        socketio.emit('admin_location_stream', payload, room="admin_dashboard")

    return jsonify({'success': True, 'recorded_at': loc.recorded_at.isoformat()}), 200


@location_bp.route('/api/location/current/<string:target_user_id>', methods=['GET'])
@jwt_required()
def get_current_location(target_user_id):
    """Retrieve latest GPS location if authorized"""
    requester_id = g.user_id
    role = g.current_role

    # Permission verification
    if role == 'SAHELI' and requester_id != target_user_id:
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    elif role == 'GUARDIAN':
        link = GuardianUser.query.filter_by(saheli_id=target_user_id, guardian_id=requester_id).first()
        if not link or not link.can_view_location:
            return jsonify({'success': False, 'error': 'Guardian does not have location viewing permission'}), 403

    loc = LocationHistory.query.filter_by(user_id=target_user_id).order_by(LocationHistory.recorded_at.desc()).first()
    if not loc:
        return jsonify({'success': False, 'error': 'No location data available'}), 404

    return jsonify({'success': True, 'location': loc.to_dict()}), 200


@location_bp.route('/api/location/history/<string:target_user_id>', methods=['GET'])
@jwt_required()
def get_location_history(target_user_id):
    """Retrieve GPS breadcrumb trail history"""
    requester_id = g.user_id
    role = g.current_role

    if role == 'SAHELI' and requester_id != target_user_id:
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    elif role == 'GUARDIAN':
        link = GuardianUser.query.filter_by(saheli_id=target_user_id, guardian_id=requester_id).first()
        if not link or not link.can_view_location:
            return jsonify({'success': False, 'error': 'Guardian does not have location viewing permission'}), 403

    limit = min(int(request.args.get('limit', 50)), 200)
    records = LocationHistory.query.filter_by(user_id=target_user_id)\
        .order_by(LocationHistory.recorded_at.desc())\
        .limit(limit)\
        .all()

    return jsonify({
        'success': True,
        'count': len(records),
        'history': [r.to_dict() for r in reversed(records)]
    }), 200


@location_bp.route('/track/<string:token_str>/api', methods=['GET'])
def get_tracking_api(token_str):
    """JSON API endpoint for real-time polling from the public tracking page"""
    token_record = TrackingToken.query.filter_by(token_value=token_str, is_revoked=False).first()
    if not token_record or token_record.expires_at < datetime.utcnow():
        return jsonify({'success': False, 'error': 'Session expired or revoked'}), 404

    session = token_record.session
    incident = session.incident
    user = incident.user

    latest_loc = LocationHistory.query.filter_by(user_id=user.id).order_by(LocationHistory.recorded_at.desc()).first()
    recent_locs = LocationHistory.query.filter_by(user_id=user.id)\
        .order_by(LocationHistory.recorded_at.desc())\
        .limit(20)\
        .all()

    breadcrumb = [[float(p.latitude), float(p.longitude)] for p in reversed(recent_locs)]

    return jsonify({
        'success': True,
        'incident': {
            'id': incident.id,
            'status': incident.status,
            'trigger_type': incident.trigger_type,
            'started_at': incident.started_at.isoformat() if incident.started_at else None,
            'battery_percent': latest_loc.battery_level if latest_loc else incident.battery_percent
        },
        'user': {
            'name': user.name
        },
        'current_location': {
            'latitude': float(latest_loc.latitude) if latest_loc else float(incident.latitude),
            'longitude': float(latest_loc.longitude) if latest_loc else float(incident.longitude),
            'accuracy': float(latest_loc.accuracy) if latest_loc else 10.0,
            'speed': float(latest_loc.speed) if latest_loc else 0.0,
            'recorded_at': latest_loc.recorded_at.isoformat() if latest_loc else None
        },
        'breadcrumb': breadcrumb
    }), 200


@location_bp.route('/track/<string:token_str>', methods=['GET'])
def public_live_tracking_page(token_str):
    """Mobile-friendly browser tracking page for emergency contacts without app"""
    token_record = TrackingToken.query.filter_by(token_value=token_str, is_revoked=False).first()
    if not token_record or token_record.expires_at < datetime.utcnow():
        return "<h3>🚨 SafeRoute Saheli: Tracking Link Expired or Invalid</h3><p>This tracking session has ended or been revoked.</p>", 404

    token_record.access_count += 1
    token_record.last_accessed_at = datetime.utcnow()
    db.session.commit()

    session = token_record.session
    incident = session.incident
    user = session.incident.user

    latest_loc = LocationHistory.query.filter_by(user_id=user.id).order_by(LocationHistory.recorded_at.desc()).first()
    lat = float(latest_loc.latitude) if latest_loc else float(incident.latitude)
    lng = float(latest_loc.longitude) if latest_loc else float(incident.longitude)

    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SafeRoute Saheli - Emergency Live Tracking</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
            body {{ background: #F5F7FA; color: #002350; }}
            .header {{ background: #002350; color: #FFFFFF; padding: 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #D2AE39; }}
            .status-banner {{ background: #DC2626; color: white; padding: 12px; font-weight: bold; text-align: center; animation: pulse 2s infinite; }}
            @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.8; }} }}
            .info-card {{ background: white; margin: 12px; padding: 16px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .badge {{ display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; background: #FEF3C7; color: #B45309; }}
            #map {{ height: 50vh; width: 100%; border-radius: 12px; }}
            .actions {{ display: flex; gap: 8px; margin-top: 12px; }}
            .action-btn {{ flex: 1; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; }}
            .btn-primary {{ background: #002350; color: #D2AE39; }}
            .btn-danger {{ background: #DC2626; color: white; }}
            .live-dot {{ display: inline-block; width: 8px; height: 8px; background: #10B981; border-radius: 50%; margin-right: 4px; animation: blink 1s infinite; }}
            @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>SafeRoute Saheli</h2>
            <span style="color: #D2AE39; font-weight: bold;"><span class="live-dot"></span>LIVE TRACKING</span>
        </div>
        <div class="status-banner" id="banner">
            🚨 EMERGENCY ACTIVE - {incident.trigger_type} TRIGGER
        </div>
        <div class="info-card">
            <h3>Saheli: {user.name}</h3>
            <p style="margin-top: 4px; color: #4B5563;">Status: <strong id="status">{incident.status}</strong> | Battery: <strong id="batt">{latest_loc.battery_level if latest_loc else incident.battery_percent}%</strong></p>
            <p style="margin-top: 4px; color: #4B5563;">Last Update: <span id="time">{datetime.utcnow().strftime('%H:%M:%S UTC')}</span></p>
            <div class="actions">
                <a class="action-btn btn-primary" id="gmaps-btn" href="https://maps.google.com/?q={lat},{lng}" target="_blank">Google Maps</a>
                <a class="action-btn btn-danger" href="tel:112">Call Police (112)</a>
            </div>
        </div>
        <div style="padding: 0 12px;">
            <div id="map"></div>
        </div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            var lat = {lat};
            var lng = {lng};
            var map = L.map('map').setView([lat, lng], 16);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            var marker = L.marker([lat, lng]).addTo(map).bindPopup('<b>{user.name}</b><br>Current Live Position').openPopup();
            var polyline = L.polyline([], {{color: '#DC2626', weight: 4, opacity: 0.8}}).addTo(map);

            // Dynamic polling every 3.5s
            setInterval(function() {{
                fetch('/track/{token_str}/api')
                    .then(res => res.json())
                    .then(data => {{
                        if (data.success && data.current_location) {{
                            var newLat = data.current_location.latitude;
                            var newLng = data.current_location.longitude;
                            marker.setLatLng([newLat, newLng]);
                            map.panTo([newLat, newLng]);
                            document.getElementById('gmaps-btn').href = 'https://maps.google.com/?q=' + newLat + ',' + newLng;
                            document.getElementById('status').innerText = data.incident.status;
                            document.getElementById('batt').innerText = data.incident.battery_percent + '%';
                            document.getElementById('time').innerText = new Date().toLocaleTimeString();
                            if (data.breadcrumb && data.breadcrumb.length > 0) {{
                                polyline.setLatLngs(data.breadcrumb);
                            }}
                        }}
                    }})
                    .catch(err => console.error('Tracking poll error:', err));
            }}, 3500);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_page)

