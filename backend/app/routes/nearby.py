import math
from flask import Blueprint, request, jsonify
from backend.app.models.routing import SafePlace

nearby_bp = Blueprint('nearby', __name__, url_prefix='/api/nearby')

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points on the Earth (meters)"""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@nearby_bp.route('/police', methods=['GET'])
def get_nearby_police():
    """Retrieve verified police stations sorted by distance from current coordinates"""
    lat = float(request.args.get('lat', 28.6139))
    lng = float(request.args.get('lng', 77.2090))
    radius_m = float(request.args.get('radius_meters', 5000))

    places = SafePlace.query.filter_by(category='POLICE', verified_status=True).all()
    results = []

    for p in places:
        dist = haversine_distance(lat, lng, float(p.latitude), float(p.longitude))
        if dist <= radius_m:
            item = p.to_dict()
            item['distance_meters'] = round(dist, 1)
            item['estimated_time_mins'] = round((dist / 1000) / 4.5 * 60, 1)  # walking speed ~4.5 km/h
            results.append(item)

    results.sort(key=lambda x: x['distance_meters'])
    return jsonify({'success': True, 'count': len(results), 'places': results}), 200


@nearby_bp.route('/hospitals', methods=['GET'])
def get_nearby_hospitals():
    """Retrieve verified hospitals sorted by distance"""
    lat = float(request.args.get('lat', 28.6139))
    lng = float(request.args.get('lng', 77.2090))
    radius_m = float(request.args.get('radius_meters', 5000))

    places = SafePlace.query.filter_by(category='HOSPITAL', verified_status=True).all()
    results = []

    for p in places:
        dist = haversine_distance(lat, lng, float(p.latitude), float(p.longitude))
        if dist <= radius_m:
            item = p.to_dict()
            item['distance_meters'] = round(dist, 1)
            item['estimated_time_mins'] = round((dist / 1000) / 4.5 * 60, 1)
            results.append(item)

    results.sort(key=lambda x: x['distance_meters'])
    return jsonify({'success': True, 'count': len(results), 'places': results}), 200


@nearby_bp.route('/safe-places', methods=['GET'])
def get_all_safe_places():
    """Retrieve all nearby verified safe points (Police, Hospitals, Shelters, Pharmacies)"""
    lat = float(request.args.get('lat', 28.6139))
    lng = float(request.args.get('lng', 77.2090))
    radius_m = float(request.args.get('radius_meters', 6000))
    category = request.args.get('category')

    query = SafePlace.query.filter_by(verified_status=True)
    if category:
        query = query.filter_by(category=category.upper())

    places = query.all()
    results = []

    for p in places:
        dist = haversine_distance(lat, lng, float(p.latitude), float(p.longitude))
        if dist <= radius_m:
            item = p.to_dict()
            item['distance_meters'] = round(dist, 1)
            results.append(item)

    results.sort(key=lambda x: x['distance_meters'])
    return jsonify({'success': True, 'count': len(results), 'places': results}), 200


@nearby_bp.route('/all', methods=['GET'])
def get_all_nearby_categorized():
    """Retrieve all nearby emergency services categorized with summary counts"""
    lat = float(request.args.get('lat', 28.6139))
    lng = float(request.args.get('lng', 77.2090))
    radius_m = float(request.args.get('radius_meters', 10000))

    places = SafePlace.query.filter_by(verified_status=True).all()
    grouped = {
        'police': [],
        'hospitals': [],
        'shelters': [],
        'pharmacies': [],
        'other': []
    }

    for p in places:
        dist = haversine_distance(lat, lng, float(p.latitude), float(p.longitude))
        if dist <= radius_m:
            item = p.to_dict()
            item['distance_meters'] = round(dist, 1)
            item['estimated_time_mins'] = round((dist / 1000) / 4.5 * 60, 1)

            cat = (p.category or '').upper()
            if 'POLICE' in cat:
                grouped['police'].append(item)
            elif 'HOSPITAL' in cat:
                grouped['hospitals'].append(item)
            elif 'SHELTER' in cat or 'ONE_STOP' in cat:
                grouped['shelters'].append(item)
            elif 'PHARMACY' in cat:
                grouped['pharmacies'].append(item)
            else:
                grouped['other'].append(item)

    # Sort each list by distance
    for key in grouped:
        grouped[key].sort(key=lambda x: x['distance_meters'])

    return jsonify({
        'success': True,
        'center': {'latitude': lat, 'longitude': lng},
        'radius_meters': radius_m,
        'summary': {
            'police_count': len(grouped['police']),
            'hospital_count': len(grouped['hospitals']),
            'shelter_count': len(grouped['shelters']),
            'pharmacy_count': len(grouped['pharmacies']),
            'total_places': sum(len(lst) for lst in grouped.values())
        },
        'places': grouped
    }), 200

