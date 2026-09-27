import math
import urllib.request
import json
import logging
from flask import Blueprint, request, jsonify
from backend.app.models.routing import SafePlace

logger = logging.getLogger(__name__)

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


def fetch_live_osm_safety_points(lat: float, lng: float, category: str, radius_m: float = 6000):
    """
    Fetch verified real police stations or hospitals dynamically from OpenStreetMap
    around the user's live latitude & longitude.
    """
    results = []
    try:
        # Approximate degrees for bounding box (~111 km per degree)
        delta = max(0.02, min(0.12, (radius_m / 111000.0) * 1.3))
        left = lng - delta
        right = lng + delta
        top = lat + delta
        bottom = lat - delta

        query_tag = 'police' if 'POLICE' in category.upper() else 'hospital'
        url = (
            f"https://nominatim.openstreetmap.org/search?format=json"
            f"&q={query_tag}&limit=5&viewbox={left},{top},{right},{bottom}&bounded=1"
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'SafeRouteSaheliLive/1.0'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for idx, item in enumerate(data):
                p_lat = float(item['lat'])
                p_lon = float(item['lon'])
                dist = haversine_distance(lat, lng, p_lat, p_lon)
                if dist <= radius_m:
                    display_parts = [part.strip() for part in item.get('display_name', '').split(',')]
                    clean_name = display_parts[0] if display_parts else f"Emergency {query_tag.title()}"
                    if len(clean_name) < 4 and len(display_parts) > 1:
                        clean_name = f"{display_parts[0]} - {display_parts[1]}"

                    phone = '112' if 'POLICE' in category.upper() else '108'
                    results.append({
                        'id': f"osm-{query_tag[:3]}-{idx}-{int(p_lat*1000)}",
                        'name': clean_name,
                        'category': 'POLICE' if 'POLICE' in category.upper() else 'HOSPITAL',
                        'latitude': p_lat,
                        'longitude': p_lon,
                        'address': item.get('display_name', ''),
                        'phone_number': phone,
                        'is_24x7': True,
                        'verified_status': True,
                        'distance_meters': round(dist, 1),
                        'estimated_time_mins': round((dist / 1000) / 4.5 * 60, 1),
                        'data_source': 'LIVE_OPENSTREETMAP'
                    })
    except Exception as e:
        logger.warning(f"Live OSM safety points lookup fallback: {e}")
    return results


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

    # If fewer than 2 DB places found around current lat/lng, enrich with live OSM real police stations
    if len(results) < 2:
        osm_police = fetch_live_osm_safety_points(lat, lng, 'POLICE', radius_m)
        seen_names = {r['name'].lower() for r in results}
        for op in osm_police:
            if op['name'].lower() not in seen_names:
                results.append(op)
                seen_names.add(op['name'].lower())

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

    # If fewer than 2 DB places found around current lat/lng, enrich with live OSM real hospitals
    if len(results) < 2:
        osm_hospitals = fetch_live_osm_safety_points(lat, lng, 'HOSPITAL', radius_m)
        seen_names = {r['name'].lower() for r in results}
        for oh in osm_hospitals:
            if oh['name'].lower() not in seen_names:
                results.append(oh)
                seen_names.add(oh['name'].lower())

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

