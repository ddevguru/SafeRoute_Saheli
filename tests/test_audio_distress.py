import unittest
import numpy as np
import io
import wave
from backend.app import create_app
from backend.app.database import db
from ai_ml.models.audio_anomaly_detector import AudioAnomalyDetector, get_audio_detector

class AudioDistressTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.detector = get_audio_detector()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _generate_sine_wave(self, freq: float, duration: float = 0.5, sample_rate: int = 16000, amp: float = 0.8) -> np.ndarray:
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)

    def _generate_wav_bytes(self, signal: np.ndarray, sample_rate: int = 16000) -> bytes:
        buf = io.BytesIO()
        int16_sig = (signal * 32767.0).astype(np.int16)
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(int16_sig.tobytes())
        return buf.getvalue()

    def test_feature_extraction(self):
        """Verify RMS, ZCR, Spectral Centroid, and Peak feature computation"""
        sig = self._generate_sine_wave(freq=3000.0, amp=0.9)
        features = self.detector.extract_features(sig)

        self.assertIn('peak', features)
        self.assertIn('rms', features)
        self.assertIn('zcr', features)
        self.assertIn('spectral_centroid', features)
        self.assertGreater(features['peak'], 0.8)
        self.assertGreater(features['spectral_centroid'], 2500.0)

    def test_scream_classification(self):
        """Screams (high pitch >2200Hz, high peak, high RMS) must trigger emergency"""
        features = {
            'peak': 0.85,
            'rms': 0.35,
            'zcr': 0.20,
            'spectral_centroid': 2900.0
        }
        res = self.detector.classify_audio(features)
        self.assertEqual(res['classification'], 'SCREAM_OR_SHOUT')
        self.assertTrue(res['is_emergency'])
        self.assertGreaterEqual(res['confidence'], 0.80)

    def test_glass_break_classification(self):
        """Glass break / crash signature"""
        features = {
            'peak': 0.95,
            'rms': 0.20,
            'zcr': 0.45,
            'spectral_centroid': 3500.0
        }
        res = self.detector.classify_audio(features)
        self.assertEqual(res['classification'], 'GLASS_BREAK_OR_CRASH')
        self.assertTrue(res['is_emergency'])

    def test_ambient_noise_non_emergency(self):
        """Low ambient noise must not trigger emergency"""
        features = {
            'peak': 0.10,
            'rms': 0.02,
            'zcr': 0.05,
            'spectral_centroid': 500.0
        }
        res = self.detector.classify_audio(features)
        self.assertEqual(res['classification'], 'AMBIENT_NOISE')
        self.assertFalse(res['is_emergency'])

    def test_api_audio_analyze_features(self):
        """POST /api/audio/analyze with JSON features"""
        payload = {
            'peak': 0.88,
            'rms': 0.40,
            'zcr': 0.18,
            'spectral_centroid': 2600.0
        }
        resp = self.client.post('/api/audio/analyze', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['result']['classification'], 'SCREAM_OR_SHOUT')
        self.assertTrue(data['result']['is_emergency'])

    def test_api_audio_analyze_wav_file(self):
        """POST /api/audio/analyze with multipart WAV audio upload"""
        sig = self._generate_sine_wave(freq=3200.0, amp=0.95, duration=0.4)
        wav_bytes = self._generate_wav_bytes(sig)

        data = {
            'audio': (io.BytesIO(wav_bytes), 'distress.wav', 'audio/wav')
        }
        resp = self.client.post('/api/audio/analyze', data=data, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 200)
        res = resp.get_json()
        self.assertTrue(res['success'])
        self.assertIn('classification', res['result'])
        self.assertIn('confidence', res['result'])

    def test_api_audio_keyword_distress(self):
        """POST /api/audio/keyword for distress phrases"""
        for phrase in ['HELP', 'SAVE ME', 'BACHAO', 'EMERGENCY', 'SAHELI HELP']:
            resp = self.client.post('/api/audio/keyword', json={'phrase': phrase})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data['matched'])
            self.assertTrue(data['is_emergency'])
            self.assertGreaterEqual(data['confidence'], 0.85)

        # Benign speech
        resp = self.client.post('/api/audio/keyword', json={'phrase': 'HELLO HOW ARE YOU'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data['matched'])
        self.assertFalse(data['is_emergency'])

    def test_api_ai_clap_detection(self):
        """POST /api/ai/clap-detection validating 3-clap pattern"""
        # Valid 3 claps
        resp = self.client.post('/api/ai/clap-detection', json={
            'clap_count': 3,
            'intervals_ms': [350, 420]
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['is_emergency_clap'])
        self.assertGreaterEqual(data['confidence'], 0.90)

        # Insufficient clap count
        resp = self.client.post('/api/ai/clap-detection', json={
            'clap_count': 1,
            'intervals_ms': []
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data['is_emergency_clap'])

    def test_api_ai_emergency_classification(self):
        """POST /api/ai/emergency-classification multi-sensor arbitration"""
        # Fall + Scream
        resp = self.client.post('/api/ai/emergency-classification', json={
            'accel_magnitude': 3.2,
            'gyro_magnitude': 220.0,
            'voice_confidence': 0.90,
            'touch_active': False,
            'clap_detected': False
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['emergency_detected'])
        self.assertEqual(data['classification'], 'MULTI_SIGNAL_EMERGENCY')
        self.assertTrue(data['signals']['is_fall'])

if __name__ == '__main__':
    unittest.main()
