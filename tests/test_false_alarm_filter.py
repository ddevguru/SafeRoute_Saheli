"""
SafeRoute Saheli — Test Suite for Phase 32:
AI Real-Time False Alarm Suppression & Smart Cancel Watchdog
"""

import unittest
from datetime import datetime, timedelta
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.emergency import EmergencyIncident
from backend.app.services.emergency_service import EmergencyService
from backend.app.services.smart_cancel_service import SmartCancelService
from ai_ml.models.false_alarm_filter import get_false_alarm_filter, FalseAlarmFilter

class TestFalseAlarmFilterAndSmartCancel(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli user
        self.saheli = User(
            name="Pooja Sharma",
            email="pooja.smartcancel@saheli.org",
            phone="+919876543232",
            is_active=True
        )
        self.saheli.set_password("SaheliSecure@123")
        db.session.add(self.saheli)
        db.session.commit()

        self.filter = get_false_alarm_filter()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_gait_regularity_walking_vs_struggle(self):
        """Verify gait regularity classifier distinguishes walking from violent struggle"""
        # 1. Normal human walking cadence samples (smooth oscillation around 1.0g)
        walking_samples = [
            {'accel_mag': 1.05, 'gyro_mag': 15.0},
            {'accel_mag': 1.18, 'gyro_mag': 22.0},
            {'accel_mag': 0.95, 'gyro_mag': 18.0},
            {'accel_mag': 1.12, 'gyro_mag': 20.0},
            {'accel_mag': 1.02, 'gyro_mag': 14.0}
        ]
        walk_eval = self.filter.evaluate_gait_regularity(walking_samples)
        self.assertGreaterEqual(walk_eval["stability_score"], 0.85)
        self.assertEqual(walk_eval["motion_state"], "REGULAR_GAIT_WALKING")
        self.assertFalse(walk_eval["is_struggle"])

        # 2. Violent physical struggle (high gyro dps & chaotic acceleration)
        struggle_samples = [
            {'accel_mag': 2.4, 'gyro_mag': 280.0},
            {'accel_mag': 0.6, 'gyro_mag': 340.0},
            {'accel_mag': 2.9, 'gyro_mag': 310.0},
            {'accel_mag': 1.8, 'gyro_mag': 250.0}
        ]
        struggle_eval = self.filter.evaluate_gait_regularity(struggle_samples)
        self.assertLessEqual(struggle_eval["stability_score"], 0.15)
        self.assertTrue(struggle_eval["is_struggle"] or struggle_eval["is_fall_shock"])
        self.assertEqual(struggle_eval["motion_state"], "VIOLENT_STRUGGLE_OR_FALL")

    def test_biometric_recovery_evaluation(self):
        """Verify vital sign panic evaluation for recovery vs acute shock"""
        # Normal calm heart rate recovery
        calm_bio = self.filter.evaluate_biometric_recovery(heart_rate_bpm=78.0, baseline_bpm=75.0, stress_score=15.0)
        self.assertGreaterEqual(calm_bio["stability_score"], 0.85)
        self.assertEqual(calm_bio["state"], "CALM_NORMAL")

        # Acute panic tachycardia
        panic_bio = self.filter.evaluate_biometric_recovery(heart_rate_bpm=138.0, baseline_bpm=75.0, stress_score=88.0)
        self.assertLessEqual(panic_bio["stability_score"], 0.15)
        self.assertEqual(panic_bio["state"], "ACUTE_PANIC_TACHYCARDIA")

    def test_speech_intent_cancellation_vs_duress(self):
        """Verify verbal transcript intent: safe cancel vs covert duress"""
        # Safe cancel transcript (Hindi / Hinglish)
        cancel_eval = self.filter.classify_speech_intent("Sorry galti se dab gaya, i am safe")
        self.assertEqual(cancel_eval["intent"], "CANCEL")
        self.assertFalse(cancel_eval["is_duress"])

        # Coercion / Duress transcript
        duress_eval = self.filter.classify_speech_intent("Please cancel it dont hurt me leave me")
        self.assertEqual(duress_eval["intent"], "DURESS")
        self.assertTrue(duress_eval["is_duress"])

    def test_dual_pin_security_logic(self):
        """Verify normal PIN disarm vs covert duress PIN trigger"""
        # Expected PIN is 1234
        status, valid = self.filter.verify_pin("1234", expected_pin="1234")
        self.assertTrue(valid)
        self.assertEqual(status, "VALID_CANCEL")

        # Universal duress PIN 9999
        status_duress, valid_duress = self.filter.verify_pin("9999", expected_pin="1234")
        self.assertTrue(valid_duress)
        self.assertEqual(status_duress, "DURESS_TRIGGERED")

        # Reverse PIN 4321 (automatic duress code)
        status_rev, valid_rev = self.filter.verify_pin("4321", expected_pin="1234")
        self.assertTrue(valid_rev)
        self.assertEqual(status_rev, "DURESS_TRIGGERED")

        # Incorrect PIN
        status_bad, valid_bad = self.filter.verify_pin("7777", expected_pin="1234")
        self.assertFalse(valid_bad)
        self.assertEqual(status_bad, "INVALID_PIN")

    def test_fused_false_alarm_assessment(self):
        """Verify holistic multi-factor Bayesian false alarm fusion"""
        walking_samples = [{'accel_mag': 1.05, 'gyro_mag': 15.0}, {'accel_mag': 1.1, 'gyro_mag': 20.0}]

        # Scenario A: Calm walking, normal HR, verbal "galti se press hua"
        result_calm = self.filter.assess_false_alarm(
            motion_samples=walking_samples,
            heart_rate_bpm=76.0,
            baseline_bpm=75.0,
            stress_score=18.0,
            speech_transcript="Galti se button press ho gaya",
            elapsed_seconds=4.0
        )
        self.assertGreaterEqual(result_calm["false_alarm_probability"], 0.80)
        self.assertIn(result_calm["recommendation"], ["CONFIRM_SAFE", "REQUIRE_PIN"])
        self.assertFalse(result_calm["is_duress"])

        # Scenario B: Coercion / Duress keyword spoken
        result_duress = self.filter.assess_false_alarm(
            motion_samples=walking_samples,
            heart_rate_bpm=120.0,
            speech_transcript="Chhod do mujhe, cancel karo",
            elapsed_seconds=5.0
        )
        self.assertEqual(result_duress["false_alarm_probability"], 0.0)
        self.assertEqual(result_duress["recommendation"], "SILENT_DURESS")
        self.assertTrue(result_duress["is_duress"])

    def test_smart_cancel_service_normal_cancel(self):
        """End-to-end test of normal false alarm disarm via SmartCancelService"""
        # Trigger an emergency first
        trigger_res = EmergencyService.trigger_emergency(
            user_id=self.saheli.id,
            trigger_type="BUTTON",
            latitude=28.6139,
            longitude=77.2090
        )
        incident_id = trigger_res["incident_id"]

        # Disarm with normal PIN 1234
        cancel_res = SmartCancelService.process_smart_cancel(
            incident_id=incident_id,
            user_id=self.saheli.id,
            entered_pin="1234",
            speech_transcript="Galti se dab gaya"
        )
        self.assertTrue(cancel_res["success"])
        self.assertEqual(cancel_res["status"], "CANCELLED_FALSE_ALARM")
        self.assertFalse(cancel_res["is_duress"])

        # Verify DB status
        incident = EmergencyIncident.query.get(incident_id)
        self.assertEqual(incident.status, "CANCELLED_FALSE_ALARM")

    def test_smart_cancel_service_covert_duress_escalation(self):
        """End-to-end test of Covert Duress PIN disarm (deceptive UI with secret escalation)"""
        # Trigger an emergency
        trigger_res = EmergencyService.trigger_emergency(
            user_id=self.saheli.id,
            trigger_type="BUTTON",
            latitude=28.6139,
            longitude=77.2090
        )
        incident_id = trigger_res["incident_id"]

        # Enter duress PIN 9999
        cancel_res = SmartCancelService.process_smart_cancel(
            incident_id=incident_id,
            user_id=self.saheli.id,
            entered_pin="9999"
        )

        # Deceptive UI for attacker: shows disarmed
        self.assertTrue(cancel_res["success"])
        self.assertEqual(cancel_res["status"], "CANCELLED")
        self.assertTrue(cancel_res["is_duress"])
        self.assertTrue(cancel_res.get("deceptive_mode", False))

        # BUT on backend database: incident escalated to DURESS_ESCALATED!
        incident = EmergencyIncident.query.get(incident_id)
        self.assertEqual(incident.status, "DURESS_ESCALATED")
        self.assertIn("COVERT DURESS", incident.cancellation_reason)

    def test_smart_verify_rest_endpoints(self):
        """Test Flask REST endpoints for smart-verify, smart-cancel, and verification-status"""
        from backend.app.auth.jwt_handler import create_access_token
        token = create_access_token(self.saheli.id, role='SAHELI')
        headers = {'Authorization': f'Bearer {token}'}

        # 1. Trigger incident
        trigger_res = EmergencyService.trigger_emergency(
            user_id=self.saheli.id,
            trigger_type="TOUCH",
            latitude=28.6139,
            longitude=77.2090
        )
        incident_id = trigger_res["incident_id"]

        # 2. Check verification status
        status_resp = self.client.get(f'/api/emergency/{incident_id}/verification-status', headers=headers)
        self.assertEqual(status_resp.status_code, 200)
        status_data = status_resp.get_json()
        self.assertTrue(status_data["success"])
        self.assertEqual(status_data["incident_id"], incident_id)

        # 3. Call smart-verify endpoint
        verify_resp = self.client.post(
            f'/api/emergency/{incident_id}/smart-verify',
            headers=headers,
            json={
                'motion_samples': [{'accel_mag': 1.02, 'gyro_mag': 12.0}],
                'heart_rate_bpm': 76.0,
                'speech_transcript': 'galti se dab gaya'
            }
        )
        self.assertEqual(verify_resp.status_code, 200)
        verify_data = verify_resp.get_json()
        self.assertTrue(verify_data["success"])
        self.assertGreaterEqual(verify_data["assessment"]["false_alarm_probability"], 0.70)

        # 4. Call smart-cancel endpoint with valid PIN
        cancel_resp = self.client.post(
            f'/api/emergency/{incident_id}/smart-cancel',
            headers=headers,
            json={'pin': '1234'}
        )
        self.assertEqual(cancel_resp.status_code, 200)
        cancel_data = cancel_resp.get_json()
        self.assertTrue(cancel_data["success"])
        self.assertEqual(cancel_data["status"], "CANCELLED_FALSE_ALARM")


if __name__ == '__main__':
    unittest.main()
