import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident
from backend.app.auth.jwt_handler import create_access_token
from ai_ml.models.biometric_stress_detector import BiometricStressDetector, get_biometric_detector


class BiometricStressDetectorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli User
        self.user = User(
            name="Kavita Rao",
            email="kavita@saheli.org",
            phone="+919876543210"
        )
        self.user.set_password("KavitaSecure#2026")
        db.session.add(self.user)
        db.session.commit()

        # Generate JWT token
        self.token = create_access_token(identity=self.user.id, role="SAHELI")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Seed Paired ESP32 Wearable Device
        self.device = Device(
            device_id="SAHELI-WEARABLE-001",
            device_type="ESP32_WEARABLE",
            firmware_version="1.1.0",
            battery_percent=94,
            assigned_user_id=self.user.id
        )
        self.device.set_secret("wearable_esp32_hmac_shared_secret_2026")
        db.session.add(self.device)
        db.session.commit()

        self.detector = BiometricStressDetector()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_resting_baseline_calm(self):
        """Resting heart rate with healthy SpO2 yields CALM state and low stress score"""
        res = self.detector.evaluate_biometrics(
            bpm=72.0,
            spo2=98.5,
            accel_mag_g=1.0,
            user_baseline_bpm=72.0
        )
        self.assertEqual(res['state'], 'CALM')
        self.assertFalse(res['is_emergency'])
        self.assertFalse(res['is_panic_emergency'])
        self.assertLess(res['stress_score'], 35.0)

    def test_exercise_tachycardia_not_emergency(self):
        """High heart rate with vigorous movement (running > 1.55g) is classified as EXERTION, not panic"""
        res = self.detector.evaluate_biometrics(
            bpm=138.0,
            spo2=97.0,
            accel_mag_g=1.85,  # Running / sports
            user_baseline_bpm=75.0
        )
        self.assertEqual(res['state'], 'EXERTION_TACHYCARDIA')
        self.assertFalse(res['is_emergency'])
        self.assertFalse(res['is_panic_emergency'])

    def test_acute_panic_tachycardia_at_rest(self):
        """Acute tachycardia (>130 BPM) while physically stationary triggers panic emergency"""
        res = self.detector.evaluate_biometrics(
            bpm=136.0,
            spo2=97.5,
            accel_mag_g=1.02,  # Still / cornered / frightened
            user_baseline_bpm=75.0
        )
        self.assertEqual(res['state'], 'ACUTE_PANIC_TACHYCARDIA')
        self.assertTrue(res['is_emergency'])
        self.assertTrue(res['is_panic_emergency'])
        self.assertGreaterEqual(res['stress_score'], 80.0)

    def test_low_hrv_panic_surge(self):
        """Sudden BPM surge (+45 BPM) with collapsed HRV (RMSSD < 20ms) triggers panic emergency"""
        # Rapid RR intervals with low variance: e.g., 440ms, 442ms, 439ms
        rr_intervals = [440.0, 442.0, 439.0, 441.0, 440.0]
        res = self.detector.evaluate_biometrics(
            bpm=122.0,
            spo2=98.0,
            accel_mag_g=1.05,
            user_baseline_bpm=70.0,
            rr_intervals_ms=rr_intervals
        )
        self.assertEqual(res['state'], 'ACUTE_PANIC_SURGE')
        self.assertTrue(res['is_emergency'])
        self.assertTrue(res['is_panic_emergency'])

    def test_critical_hypoxia_emergency(self):
        """Desaturation below 90% triggers medical emergency"""
        res = self.detector.evaluate_biometrics(
            bpm=88.0,
            spo2=86.5,
            accel_mag_g=1.0
        )
        self.assertEqual(res['state'], 'CRITICAL_HYPOXIA')
        self.assertTrue(res['is_emergency'])
        self.assertTrue(res['is_hypoxia_emergency'])

    def test_sensor_disconnected(self):
        """Disconnected sensor does not trigger false emergency"""
        res = self.detector.evaluate_biometrics(
            bpm=0.0,
            spo2=0.0,
            is_finger_detected=False
        )
        self.assertEqual(res['state'], 'SENSOR_DISCONNECTED')
        self.assertFalse(res['is_emergency'])

    def test_api_biometric_telemetry_normal(self):
        """Posting normal biometrics via authenticated API returns successful assessment without emergency"""
        payload = {
            "heart_rate_bpm": 74.0,
            "spo2": 98.0,
            "accel_mag_g": 1.0,
            "is_finger_detected": True,
            "baseline_bpm": 72.0
        }
        resp = self.client.post('/api/emergency/biometric-telemetry', json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertFalse(data['emergency_triggered'])
        self.assertEqual(data['assessment']['state'], 'CALM')

    def test_api_biometric_panic_auto_dispatches_sos(self):
        """Posting acute tachycardia at rest auto-dispatches an SOS incident"""
        payload = {
            "heart_rate_bpm": 139.0,
            "spo2": 96.5,
            "accel_mag_g": 1.03,
            "is_finger_detected": True,
            "latitude": 28.6140,
            "longitude": 77.2092,
            "battery_percent": 91
        }
        resp = self.client.post('/api/emergency/biometric-telemetry', json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['emergency_triggered'])
        self.assertIsNotNone(data['incident'])

        # Verify DB incident record
        inc = EmergencyIncident.query.filter_by(user_id=self.user.id, status='ACTIVE').first()
        self.assertIsNotNone(inc)
        self.assertEqual(inc.trigger_type, 'BIOMETRIC_PANIC')
        self.assertAlmostEqual(float(inc.latitude), 28.6140)
        self.assertAlmostEqual(float(inc.longitude), 77.2092)

    def test_api_iot_device_biometric_auth(self):
        """IoT wearable posting biometrics using device_id + device_secret triggers emergency without user JWT"""
        payload = {
            "device_id": "SAHELI-WEARABLE-001",
            "device_secret": "wearable_esp32_hmac_shared_secret_2026",
            "heart_rate_bpm": 142.0,
            "spo2": 97.0,
            "accel_mag_g": 1.01,
            "latitude": 28.6250,
            "longitude": 77.2150,
            "battery_percent": 88
        }
        resp = self.client.post('/api/emergency/biometric-telemetry', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['emergency_triggered'])
        self.assertEqual(data['assessment']['state'], 'ACUTE_PANIC_TACHYCARDIA')

        # Check DB incident
        inc = EmergencyIncident.query.filter_by(user_id=self.user.id, status='ACTIVE').first()
        self.assertIsNotNone(inc)
        self.assertEqual(inc.trigger_type, 'BIOMETRIC_PANIC')


if __name__ == '__main__':
    unittest.main()
