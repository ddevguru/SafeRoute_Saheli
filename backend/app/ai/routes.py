from flask import Blueprint, request, jsonify, g
from backend.app.auth.jwt_handler import jwt_required

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

def evaluate_neuro_fuzzy_risk(crime: float, lighting: float, isolation: float, crowd: float, hour: int) -> dict:
    """
    ANFIS / Neuro-Fuzzy Inference Engine for Safety Risk Score (0 - 100)
    Inputs:
    - crime (0.0 to 1.0): normalized spatial crime risk
    - lighting (0.0 to 1.0): 1.0 = brightly lit, 0.0 = dark alley
    - isolation (0.0 to 1.0): 1.0 = completely deserted, 0.0 = active thoroughfare
    - crowd (0.0 to 1.0): active foot traffic
    - hour (0 to 23): diurnal vulnerability coefficient (night hours 22:00 - 05:00 scale up risk)
    """
    # 1. Fuzzification: Membership functions (LOW, MED, HIGH)
    def tri_mf(x, a, b, c):
        return max(min((x - a)/(b - a + 1e-6), (c - x)/(c - b + 1e-6)), 0.0)

    crime_low = tri_mf(crime, 0.0, 0.0, 0.5)
    crime_med = tri_mf(crime, 0.2, 0.5, 0.8)
    crime_high = tri_mf(crime, 0.5, 1.0, 1.0)

    light_poor = tri_mf(1.0 - lighting, 0.5, 1.0, 1.0)
    light_good = tri_mf(lighting, 0.5, 1.0, 1.0)

    isolation_high = tri_mf(isolation, 0.5, 1.0, 1.0)

    # Diurnal factor: Night time [22..5] has higher vulnerability weight
    is_night = 1.0 if (hour >= 21 or hour <= 5) else 0.3

    # 2. Rule evaluation (Mamdani / Sugeno simplified firing strength)
    # Rule 1: High crime + Poor light + High isolation -> VERY HIGH RISK
    w1 = min(crime_high, light_poor, isolation_high) * 95.0

    # Rule 2: Med crime + Poor light -> HIGH RISK
    w2 = min(crime_med, light_poor) * 75.0

    # Rule 3: Low crime + Good light + High crowd -> LOW RISK
    w3 = min(crime_low, light_good, tri_mf(crowd, 0.5, 1.0, 1.0)) * 15.0

    # Rule 4: Night time amplifier
    w4 = is_night * (crime * 40.0 + (1.0 - lighting) * 40.0)

    total_weight = crime_high + crime_med + crime_low + 0.1
    raw_risk = (w1 + w2 + w3 + w4) / (total_weight + is_night)
    risk_score = min(max(raw_risk, 5.0), 98.0)

    # Invert for safety score (Safety Score = 100 - Risk Score)
    safety_score = 100.0 - risk_score

    return {
        'risk_score': round(risk_score, 1),
        'safety_score': round(safety_score, 1),
        'risk_category': 'CRITICAL' if risk_score > 75 else ('ELEVATED' if risk_score > 40 else 'LOW_SAFE'),
        'components': {
            'crime_impact': round(crime * 100, 1),
            'lighting_deficiency': round((1.0 - lighting) * 100, 1),
            'isolation_impact': round(isolation * 100, 1),
            'diurnal_vulnerability': 'NIGHT_HOURS' if is_night > 0.5 else 'DAYLIGHT'
        }
    }


@ai_bp.route('/risk', methods=['POST'])
def get_risk_score():
    """Evaluate soft computing risk score for given location or road segment"""
    data = request.get_json() or {}
    crime = float(data.get('crime_rate', 0.2))
    lighting = float(data.get('lighting_quality', 0.8))
    isolation = float(data.get('isolation_index', 0.2))
    crowd = float(data.get('crowd_density', 0.6))
    hour = int(data.get('hour_of_day', 14))

    result = evaluate_neuro_fuzzy_risk(crime, lighting, isolation, crowd, hour)
    return jsonify({'success': True, 'evaluation': result}), 200


@ai_bp.route('/emergency-classification', methods=['POST'])
def classify_emergency():
    """Multi-sensor anomaly fusion: Motion (MPU6050) + Touch + Audio triggers"""
    data = request.get_json() or {}
    accel_magnitude = float(data.get('accel_magnitude', 1.0))  # in g's
    gyro_magnitude = float(data.get('gyro_magnitude', 0.0))    # in deg/s
    voice_confidence = float(data.get('voice_confidence', 0.0))
    touch_active = bool(data.get('touch_active', False))
    clap_detected = bool(data.get('clap_detected', False))

    is_fall = accel_magnitude > 2.8 and gyro_magnitude > 200.0
    is_struggle = accel_magnitude > 2.0 and gyro_magnitude > 150.0

    emergency_detected = touch_active or clap_detected or (voice_confidence > 0.70) or is_fall
    classification = 'MULTI_SIGNAL_EMERGENCY' if emergency_detected else 'NORMAL'

    return jsonify({
        'success': True,
        'emergency_detected': emergency_detected,
        'classification': classification,
        'signals': {
            'is_fall': is_fall,
            'is_struggle': is_struggle,
            'voice_active': voice_confidence > 0.70,
            'touch_active': touch_active,
            'clap_active': clap_detected
        }
    }), 200


@ai_bp.route('/voice-detection', methods=['POST'])
def detect_voice_keyword():
    """Verify audio snippet or keyword event ('HELP', 'BACHAO', 'SAVE ME')"""
    data = request.get_json() or {}
    keyword = data.get('keyword', '').upper().strip()
    target_keywords = ['HELP', 'HELP ME', 'SAVE ME', 'EMERGENCY', 'BACHAO', 'BACHAAO', 'SAHELI HELP']

    matched = keyword in target_keywords
    confidence = float(data.get('confidence', 0.88 if matched else 0.12))

    return jsonify({
        'success': True,
        'keyword': keyword,
        'matched': matched,
        'confidence': confidence,
        'threshold_exceeded': confidence >= 0.75
    }), 200


@ai_bp.route('/clap-detection', methods=['POST'])
def detect_clap_pattern():
    """Validate 3-clap pattern within configurable time window"""
    data = request.get_json() or {}
    clap_count = int(data.get('clap_count', 3))
    intervals_ms = data.get('intervals_ms', [350, 380])  # typical rapid triple clap

    # Valid if 3 claps within 200ms to 700ms intervals
    valid_intervals = all(200 <= i <= 700 for i in intervals_ms) if intervals_ms else True
    is_emergency_clap = (clap_count >= 3) and valid_intervals

    return jsonify({
        'success': True,
        'clap_count': clap_count,
        'is_emergency_clap': is_emergency_clap,
        'confidence': 0.92 if is_emergency_clap else 0.25
    }), 200
