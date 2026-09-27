import os
import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from backend.app.database import db
from backend.app.models.evidence import AudioRecording
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident
from backend.app.auth.jwt_handler import jwt_required

audio_bp = Blueprint('audio', __name__, url_prefix='/api/audio')

@audio_bp.route('/upload', methods=['POST'])
def upload_audio():
    """Upload audio evidence recorded by wearable INMP441 microphone or mobile app"""
    device_id = request.form.get('device_id') or request.headers.get('X-Device-Id')
    device_secret = request.form.get('device_secret') or request.headers.get('X-Device-Secret')

    device = Device.query.filter_by(device_id=device_id).first()
    if not device or not device.verify_secret(device_secret or ''):
        return jsonify({'success': False, 'error': 'Unauthorized device'}), 401

    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file found'}), 400

    audio_file = request.files['audio']
    audio_bytes = audio_file.read()
    file_hash = hashlib.sha256(audio_bytes).hexdigest()

    duration = int(request.form.get('duration', 10))
    trigger_type = request.form.get('trigger_type', 'EMERGENCY')

    filename = f"audio_{device_id}_{int(datetime.utcnow().timestamp())}_{file_hash[:8]}.wav"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'audio')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, 'wb') as f:
        f.write(audio_bytes)

    incident = EmergencyIncident.query.filter_by(user_id=device.assigned_user_id, status='ACTIVE').first()

    # Audio DSP Analysis
    from ai_ml.models.audio_anomaly_detector import get_audio_detector
    detector = get_audio_detector()
    analysis = None
    try:
        # If WAV audio, attempt reading raw PCM samples
        import io
        import wave
        import numpy as np
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)
            # 16-bit PCM conversion
            signal = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            analysis = detector.classify_audio(signal)
    except Exception:
        # Fallback to default classification if header parse fails
        analysis = detector.classify_audio({'peak': 0.5, 'rms': 0.1, 'zcr': 0.1, 'spectral_centroid': 1000.0})

    record = AudioRecording(
        incident_id=incident.id if incident else None,
        device_id=device.id,
        user_id=device.assigned_user_id,
        storage_url=f"/uploads/audio/{filename}",
        duration_seconds=duration,
        file_size_bytes=len(audio_bytes),
        file_hash=file_hash,
        trigger_type=trigger_type
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        'success': True,
        'audio_id': record.id,
        'storage_url': record.storage_url,
        'duration_seconds': record.duration_seconds,
        'analysis': analysis
    }), 201


@audio_bp.route('/analyze', methods=['POST'])
def analyze_audio_stream():
    """Analyze audio features or raw audio stream for distress signatures"""
    from ai_ml.models.audio_anomaly_detector import get_audio_detector
    detector = get_audio_detector()

    if request.is_json:
        data = request.get_json() or {}
        # May supply either raw 'features' dict or individual fields
        features = data.get('features')
        if not features:
            features = {
                'peak': float(data.get('peak', 0.0)),
                'rms': float(data.get('rms', 0.0)),
                'zcr': float(data.get('zcr', 0.0)),
                'spectral_centroid': float(data.get('spectral_centroid', 0.0))
            }
        result = detector.classify_audio(features)
        return jsonify({'success': True, 'result': result}), 200

    if 'audio' in request.files:
        audio_file = request.files['audio']
        audio_bytes = audio_file.read()
        try:
            import io
            import wave
            import numpy as np
            with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
                n_frames = wf.getnframes()
                frames = wf.readframes(n_frames)
                signal = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                result = detector.classify_audio(signal)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to process audio waveform: {str(e)}'}), 400

        return jsonify({'success': True, 'result': result}), 200

    return jsonify({'success': False, 'error': 'No audio file or feature payload provided'}), 400


@audio_bp.route('/keyword', methods=['POST'])
def detect_voice_keyword():
    """Vocal keyword spotting for emergency distress phrases (English + Vernacular)"""
    from ai_ml.models.vernacular_distress_detector import get_vernacular_detector

    data = request.get_json() or {}
    phrase = str(data.get('phrase', data.get('keyword', ''))).strip()
    phrase_upper = phrase.upper()
    
    emergency_phrases = {
        'HELP': 0.95,
        'HELP ME': 0.96,
        'SAVE ME': 0.97,
        'BACHAO': 0.98,
        'BACHAAO': 0.98,
        'EMERGENCY': 0.92,
        'SAHELI HELP': 0.99
    }

    matched = False
    confidence = 0.0
    matched_phrase = None

    for target, conf in emergency_phrases.items():
        if target in phrase_upper or phrase_upper == target:
            matched = True
            confidence = max(confidence, conf)
            matched_phrase = target

    # Vernacular check if not matched by standard list
    vernacular_eval = None
    if not matched and phrase:
        detector = get_vernacular_detector()
        vernacular_eval = detector.evaluate_text_phrase(phrase)
        if vernacular_eval["is_distress"]:
            matched = True
            confidence = vernacular_eval["confidence"]
            matched_phrase = vernacular_eval["matched_keyword"]

    return jsonify({
        'success': True,
        'phrase': phrase,
        'matched': matched,
        'matched_phrase': matched_phrase,
        'confidence': round(confidence, 2) if matched else 0.10,
        'is_emergency': matched and (confidence >= 0.80),
        'vernacular_analysis': vernacular_eval
    }), 200


@audio_bp.route('/vernacular-distress', methods=['POST'])
@jwt_required(optional=True)
def detect_vernacular_distress():
    """
    Multi-Lingual Audio Distress Evaluation Endpoint:
    Processes vocal distress across Hindi, Bengali, Tamil, Telugu, Marathi, Kannada & English.
    Fuses phonetic phrase recognition with acoustic scream energy.
    """
    from ai_ml.models.vernacular_distress_detector import get_vernacular_detector
    from backend.app.services.emergency_service import EmergencyService

    data = request.get_json() or {}
    phrase = data.get('phrase') or data.get('transcript') or data.get('text')
    rms = float(data.get('rms', 0.0))
    spectral_centroid = float(data.get('spectral_centroid', 0.0))
    zcr = float(data.get('zcr', 0.0))
    peak = float(data.get('peak', 0.0))
    auto_trigger = bool(data.get('auto_trigger', False))

    detector = get_vernacular_detector()
    assessment = detector.fuse_vernacular_distress(
        text_phrase=phrase,
        rms=rms,
        spectral_centroid=spectral_centroid,
        zcr=zcr,
        peak=peak
    )

    incident_result = None
    user_id = getattr(g, 'user_id', None) or data.get('user_id')

    if assessment['is_distress'] and auto_trigger and user_id:
        latitude = float(data.get('latitude', 28.6139))
        longitude = float(data.get('longitude', 77.2090))
        battery_percent = int(data.get('battery_percent', 100))
        socketio = current_app.extensions.get('socketio')

        incident_result = EmergencyService.trigger_emergency(
            user_id=user_id,
            trigger_type='VERNACULAR_VOICE',
            latitude=latitude,
            longitude=longitude,
            confidence=assessment['confidence'],
            battery_percent=battery_percent,
            socketio=socketio
        )

    return jsonify({
        'success': True,
        'assessment': assessment,
        'is_distress': assessment['is_distress'],
        'emergency_triggered': incident_result is not None,
        'incident': incident_result
    }), 200


@audio_bp.route('/<string:incident_id>', methods=['GET'])
@jwt_required()
def get_incident_audio(incident_id):
    """Retrieve audio evidence for an incident"""
    records = AudioRecording.query.filter_by(incident_id=incident_id).all()
    results = [rec.to_dict() for rec in records]
    return jsonify({'success': True, 'audio_recordings': results}), 200


