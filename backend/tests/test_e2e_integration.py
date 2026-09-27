"""
SafeRoute Saheli — Full End-to-End System Integration Test
Simulates the complete emergency lifecycle across:
1. User Registration & JWT Authentication
2. Hardware Provisioning (ESP32 Wearable & ESP32-CAM)
3. Device Pairing to Saheli Account
4. Guardian Linkage & Permission Sync
5. IoT Telemetry Heartbeat
6. IoT Hardware SOS Trigger (TTP223 / 3-Clap / Fall)
7. Automatic Notification Dispatch (FCM & SMS)
8. Camera Evidence Frame Ingestion
9. AI Safe Route Computation (ANFIS & Genetic Optimizer)
10. Admin Command Center Review & Incident Resolution
"""

import unittest
import io
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident, NotificationLog
from backend.app.models.evidence import CameraSnapshot
from backend.app.models.admin import AdminUser
from backend.app.auth.jwt_handler import create_access_token

class TestSafeRouteSaheliE2E(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_full_emergency_lifecycle_e2e(self):
        """Execute complete end-to-end multi-tier safety workflow"""

        # -------------------------------------------------------------
        # STEP 1: Saheli User Registration & Authentication
        # -------------------------------------------------------------
        reg_payload = {
            "name": "Ananya Sen",
            "email": "ananya.sen@example.com",
            "phone": "+919811122233",
            "password": "SecurePassword@2026",
            "emergency_blood_group": "A+",
            "medical_notes": "Asthma inhaler in purse"
        }
        res_reg = self.client.post('/api/auth/register', json=reg_payload)
        self.assertEqual(res_reg.status_code, 201)
        saheli_token = res_reg.get_json()['access_token']
        saheli_headers = {'Authorization': f"Bearer {saheli_token}"}

        saheli_user = User.query.filter_by(email="ananya.sen@example.com").first()
        self.assertIsNotNone(saheli_user)

        # -------------------------------------------------------------
        # STEP 2: Admin Provisions ESP32 Wearable and ESP32-CAM
        # -------------------------------------------------------------
        admin_token = create_access_token('adm-001', role='ADMIN')
        admin_headers = {'Authorization': f"Bearer {admin_token}"}

        # Provision Wearable
        res_dev1 = self.client.post('/api/devices/register', json={
            "device_id": "SAHELI-WEARABLE-001",
            "device_type": "ESP32_WEARABLE",
            "device_secret": "wearable_secret_key_123",
            "nickname": "Ananya Safety Band"
        }, headers=admin_headers)
        self.assertEqual(res_dev1.status_code, 201)

        # Provision ESP32-CAM
        res_dev2 = self.client.post('/api/devices/register', json={
            "device_id": "SAHELI-CAM-001",
            "device_type": "ESP32_CAM",
            "device_secret": "cam_secret_key_123",
            "nickname": "Ananya Optical Module"
        }, headers=admin_headers)
        self.assertEqual(res_dev2.status_code, 201)

        # -------------------------------------------------------------
        # STEP 3: Saheli Pairs Wearable and Camera to Her Account
        # -------------------------------------------------------------
        res_pair1 = self.client.post('/api/devices/pair', json={
            "device_id": "SAHELI-WEARABLE-001",
            "device_secret": "wearable_secret_key_123"
        }, headers=saheli_headers)
        self.assertEqual(res_pair1.status_code, 200)

        res_pair2 = self.client.post('/api/devices/pair', json={
            "device_id": "SAHELI-CAM-001",
            "device_secret": "cam_secret_key_123"
        }, headers=saheli_headers)
        self.assertEqual(res_pair2.status_code, 200)

        # -------------------------------------------------------------
        # STEP 4: Guardian Links to Saheli Account
        # -------------------------------------------------------------
        res_guardian = self.client.post('/api/guardians', json={
            "name": "Rajesh Sen",
            "phone": "+919822233344",
            "email": "rajesh.sen@example.com",
            "relationship": "Father",
            "can_view_camera": True,
            "emergency_override_camera": True
        }, headers=saheli_headers)
        self.assertEqual(res_guardian.status_code, 201)

        # -------------------------------------------------------------
        # STEP 5: Wearable Sends Telemetry Heartbeat
        # -------------------------------------------------------------
        res_hb = self.client.post('/api/devices/heartbeat', json={
            "device_id": "SAHELI-WEARABLE-001",
            "device_secret": "wearable_secret_key_123",
            "battery_percent": 88,
            "battery_voltage": 4.02,
            "wifi_rssi": -58
        })
        self.assertEqual(res_hb.status_code, 200)

        # -------------------------------------------------------------
        # STEP 6: Wearable Triggers Hardware SOS Event (Touch Sensor)
        # -------------------------------------------------------------
        res_sos = self.client.post('/api/emergency/trigger', json={
            "device_id": "SAHELI-WEARABLE-001",
            "device_secret": "wearable_secret_key_123",
            "trigger_type": "TOUCH",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "battery_percent": 87,
            "confidence": 1.0
        })
        self.assertEqual(res_sos.status_code, 200)
        sos_data = res_sos.get_json()
        self.assertTrue(sos_data['success'])
        incident_id = sos_data['incident_id']
        self.assertIsNotNone(incident_id)

        # Verify active incident in database
        active_inc = EmergencyIncident.query.filter_by(id=incident_id, status='ACTIVE').first()
        self.assertIsNotNone(active_inc)
        self.assertEqual(active_inc.user_id, saheli_user.id)

        # Verify SMS & notification logs recorded
        sms_logs = NotificationLog.query.filter_by(incident_id=incident_id).all()
        self.assertGreater(len(sms_logs), 0)

        # -------------------------------------------------------------
        # STEP 7: ESP32-CAM Uploads Emergency Burst Image Frame
        # -------------------------------------------------------------
        dummy_image = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
            b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4'
            b'\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00'
            b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'
        )

        res_cam = self.client.post('/api/camera/emergency-capture', data={
            'device_id': 'SAHELI-CAM-001',
            'device_secret': 'cam_secret_key_123',
            'image': (io.BytesIO(dummy_image), 'frame_01.jpg')
        }, content_type='multipart/form-data')
        self.assertEqual(res_cam.status_code, 201)

        # Verify snapshot tied to incident
        snapshot = CameraSnapshot.query.filter_by(incident_id=incident_id).first()
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.user_id, saheli_user.id)

        # -------------------------------------------------------------
        # STEP 8: Safe Routing Optimization (Genetic + ANFIS)
        # -------------------------------------------------------------
        res_routes = self.client.post('/api/routes/calculate', json={
            "start_lat": 28.6139,
            "start_lng": 77.2090,
            "dest_lat": 28.6300,
            "dest_lng": 77.2200,
            "hour_of_day": 23
        }, headers=saheli_headers)
        self.assertEqual(res_routes.status_code, 200)
        routes_data = res_routes.get_json()
        self.assertTrue(routes_data['success'])
        self.assertEqual(len(routes_data['routes']), 3)

        # -------------------------------------------------------------
        # STEP 9: Admin Reviews Emergency & Marks as Safely Resolved
        # -------------------------------------------------------------
        res_admin_emergencies = self.client.get('/api/admin/emergencies?status=ACTIVE', headers=admin_headers)
        self.assertEqual(res_admin_emergencies.status_code, 200)
        self.assertGreater(len(res_admin_emergencies.get_json()['emergencies']), 0)

        # Admin Resolves
        res_resolve = self.client.post(f'/api/emergency/{incident_id}/resolve', json={
            "notes": "Police Unit 4 reached victim. Attacker apprehended. Saheli safe."
        }, headers=admin_headers)
        self.assertEqual(res_resolve.status_code, 200)

        # Confirm incident is resolved
        resolved_inc = db.session.get(EmergencyIncident, incident_id)
        self.assertEqual(resolved_inc.status, 'RESOLVED')
        self.assertIsNotNone(resolved_inc.resolved_at)

        print("\n>>> END-TO-END SAFETY LIFECYCLE TEST PASSED COMPLETELY! <<<")


if __name__ == '__main__':
    unittest.main()
