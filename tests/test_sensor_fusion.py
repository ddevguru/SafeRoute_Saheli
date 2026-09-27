"""
SafeRoute Saheli — Multi-Modal Sensor Fusion Engine Unit & Integration Tests (Phase 28)
Validates Bayesian state estimation across Touch, Motion, Acoustic, Biometric, and ANFIS signals.
"""

import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident
from backend.app.auth.jwt_handler import create_access_token
from ai_ml.models.sensor_fusion_engine import MultiModalSensorFusionEngine, get_sensor_fusion_engine


class MultiModalSensorFusionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli User
        self.user = User(
            name="Meera Joshi",
            email="meera@saheli.org",
            phone="+919876543219"
        )
        self.user.set_password("MeeraPass#2026")
        db.session.add(self.user)
        db.session.commit()

        # JWT auth header
        self.token = create_access_token(identity=self.user.id, role="SAHELI")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Seed Paired IoT Wearable Device
        self.device = Device(
            device_id="SAHELI-FUSION-001",
            device_type="ESP32_WEARABLE",
            firmware_version="1.2.0",
            battery_percent=95,
            assigned_user_id=self.user.id
        )
        self.device.set_secret("fusion_shared_secret_2026")
        db.session.add(self.device)
        db.session.commit()

        self.engine = MultiModalSensorFusionEngine()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_baseline_safe_condition(self):
        """Normal walking during daylight with calm heart rate yields NORMAL_SECURE threat level"""
        res = self.engine.fuse_telemetry(
            touch_hold_ms=0.0,
            accel_mag_g=1.05,
            heart_rate_bpm=72.0,
            spo2=98.5,
            stress_score=15.0,
            anfis_risk_score=20.0,
            hour_of_day=14
        )
        self.assertLess(res['threat_probability'], 0.10)
        self.assertEqual(res['threat_level'], 'NORMAL_SECURE')
        self.assertFalse(res['is_emergency_triggered'])

    def test_02_continuous_touch_manual_override(self):
        """Continuous touch hold >= 1500ms triggers CRITICAL_EMERGENCY with maximum threat probability"""
        res = self.engine.fuse_telemetry(
            touch_hold_ms=1600.0,
            accel_mag_g=1.0,
            heart_rate_bpm=75.0,
            anfis_risk_score=30.0
        )
        self.assertGreaterEqual(res['threat_probability'], 0.95)
        self.assertEqual(res['threat_level'], 'CRITICAL_EMERGENCY')
        self.assertTrue(res['is_emergency_triggered'])
        self.assertIn("TOUCH_HOLD_1600MS", res['contributing_factors'])

    def test_03_coincident_multi_signal_threat_escalation(self):
        """Multiple medium signals (sub-threshold touch + tachycardia + acoustic murmur + high-risk night zone) fuse to trigger emergency"""
        res = self.engine.fuse_telemetry(
            touch_hold_ms=900.0,  # Medium hold (not 1500ms yet)
            accel_mag_g=1.02,
            is_scream=True,       # Distress sound detected
            audio_confidence=0.82,
            heart_rate_bpm=132.0, # Elevated heart rate
            is_panic_tachycardia=True,
            stress_score=85.0,
            anfis_risk_score=78.0,# High vulnerability unlit street
            hour_of_day=23        # Night time
        )
        self.assertGreaterEqual(res['threat_probability'], 0.85)
        self.assertEqual(res['threat_level'], 'CRITICAL_EMERGENCY')
        self.assertTrue(res['is_emergency_triggered'])
        self.assertGreaterEqual(res['coincident_signal_count'], 3)
        self.assertEqual(res['recommended_action'], 'FULL_POLICE_GUARDIAN_DISPATCH')

    def test_04_fall_impact_with_physical_struggle(self):
        """Severe fall impact followed by tumbling and struggle triggers high threat emergency"""
        res = self.engine.fuse_telemetry(
            accel_mag_g=3.2,      # Fall impact
            gyro_mag_dps=280.0,   # High angular struggle
            is_fall=True,
            is_struggle=True,
            is_scream=True,
            heart_rate_bpm=128.0,
            anfis_risk_score=50.0
        )
        self.assertGreaterEqual(res['threat_probability'], 0.90)
        self.assertTrue(res['is_emergency_triggered'])
        self.assertIn("FALL_IMPACT_DETECTED", res['contributing_factors'])
        self.assertIn("PHYSICAL_STRUGGLE_DETECTED", res['contributing_factors'])

    def test_05_api_sensor_fusion_normal_telemetry(self):
        """POST /api/emergency/sensor-fusion-telemetry returns normal evaluation without triggering SOS"""
        payload = {
            "touch_hold_ms": 0.0,
            "accel_mag_g": 1.02,
            "heart_rate_bpm": 74.0,
            "spo2": 98.0,
            "stress_score": 12.0,
            "anfis_risk_score": 18.0,
            "hour_of_day": 12
        }
        resp = self.client.post('/api/emergency/sensor-fusion-telemetry', json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertFalse(data['emergency_triggered'])
        self.assertEqual(data['assessment']['threat_level'], 'NORMAL_SECURE')

    def test_06_api_sensor_fusion_auto_escalates_sos(self):
        """POST /api/emergency/sensor-fusion-telemetry with high multi-signal threat automatically logs SOS incident"""
        payload = {
            "touch_hold_ms": 1600.0,
            "is_fall": True,
            "is_struggle": True,
            "is_scream": True,
            "heart_rate_bpm": 138.0,
            "is_panic_tachycardia": True,
            "stress_score": 90.0,
            "anfis_risk_score": 85.0,
            "hour_of_day": 23,
            "latitude": 28.6142,
            "longitude": 77.2098,
            "battery_percent": 87
        }
        resp = self.client.post('/api/emergency/sensor-fusion-telemetry', json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['emergency_triggered'])
        self.assertIsNotNone(data['incident'])

        # Verify active incident record in DB
        inc = EmergencyIncident.query.filter_by(user_id=self.user.id, status='ACTIVE').first()
        self.assertIsNotNone(inc)
        self.assertEqual(inc.trigger_type, 'MULTI_SENSOR_FUSION')
        self.assertAlmostEqual(float(inc.latitude), 28.6142)
        self.assertAlmostEqual(float(inc.longitude), 77.2098)

    def test_07_api_iot_device_auth_sensor_fusion(self):
        """IoT wearable posting multi-sensor telemetry using device_id + device_secret triggers emergency"""
        payload = {
            "device_id": "SAHELI-FUSION-001",
            "device_secret": "fusion_shared_secret_2026",
            "touch_hold_ms": 1800.0,
            "heart_rate_bpm": 140.0,
            "latitude": 28.6200,
            "longitude": 77.2100,
            "battery_percent": 92
        }
        resp = self.client.post('/api/emergency/sensor-fusion-telemetry', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['emergency_triggered'])

        inc = EmergencyIncident.query.filter_by(user_id=self.user.id, status='ACTIVE').first()
        self.assertIsNotNone(inc)
        self.assertEqual(inc.trigger_type, 'MULTI_SENSOR_FUSION')


if __name__ == '__main__':
    unittest.main()
