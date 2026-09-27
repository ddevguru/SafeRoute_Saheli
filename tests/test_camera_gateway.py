import unittest
import io
from datetime import datetime, timedelta
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident
from backend.app.models.evidence import CameraSnapshot
from backend.app.auth.jwt_handler import create_access_token

class CameraGatewayTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli user
        self.user = User(
            name="Priya Patel",
            email="priya@example.com",
            phone="+919876500001"
        )
        self.user.set_password("SaheliPass123!")
        db.session.add(self.user)

        # Seed Guardian
        self.guardian = Guardian(
            name="Rajesh Patel",
            username="rajesh_patel",
            email="rajesh@example.com",
            phone="+919876500002",
            relationship="FATHER"
        )
        self.guardian.set_password("FatherPass123!")
        db.session.add(self.guardian)
        db.session.commit()

        # Link Guardian with camera permissions disabled initially
        self.link = GuardianUser(
            saheli_id=self.user.id,
            guardian_id=self.guardian.id,
            relationship_label="FATHER",
            can_view_location=True,
            can_view_camera=False,
            emergency_override_camera=True
        )
        db.session.add(self.link)

        # Register ESP32-CAM Device
        self.cam_device = Device(
            device_id="SAHELI-CAM-001",
            device_type="ESP32_CAM",
            assigned_user_id=self.user.id,
            status="ONLINE",
            camera_health="HEALTHY",
            wifi_rssi=-58
        )
        self.cam_device.set_secret("esp32_cam_secret_2026")
        db.session.add(self.cam_device)
        db.session.commit()

        # JWT tokens
        self.saheli_token = create_access_token(self.user.id, 'SAHELI', {'email': self.user.email})
        self.saheli_headers = {'Authorization': f"Bearer {self.saheli_token}"}

        self.guardian_token = create_access_token(self.guardian.id, 'GUARDIAN', {'email': self.guardian.email})
        self.guardian_headers = {'Authorization': f"Bearer {self.guardian_token}"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_saheli_create_camera_session(self):
        """Saheli can generate viewing session for her own camera"""
        resp = self.client.post('/api/camera/session', json={}, headers=self.saheli_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('session_token', data)
        self.assertEqual(data['device_id'], 'SAHELI-CAM-001')
        self.assertIn('stream_url', data)

    def test_guardian_camera_privacy_denial(self):
        """Guardian denied camera viewing without permission or emergency"""
        resp = self.client.post('/api/camera/session', json={'target_user_id': self.user.id}, headers=self.guardian_headers)
        self.assertEqual(resp.status_code, 403)
        data = resp.get_json()
        self.assertFalse(data['success'])
        self.assertIn('denied', data['error'].lower())

    def test_guardian_camera_emergency_override(self):
        """Active emergency overrides privacy setting to protect user"""
        incident = EmergencyIncident(
            user_id=self.user.id,
            trigger_type='TOUCH',
            status='ACTIVE',
            latitude=28.6139,
            longitude=77.2090
        )
        db.session.add(incident)
        db.session.commit()

        resp = self.client.post('/api/camera/session', json={'target_user_id': self.user.id}, headers=self.guardian_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('session_token', data)

    def test_camera_snapshot_upload(self):
        """ESP32-CAM uploads evidence frame with cryptographic hash"""
        fake_jpg = b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\xFF\xD9'
        data = {
            'device_id': 'SAHELI-CAM-001',
            'device_secret': 'esp32_cam_secret_2026',
            'image': (io.BytesIO(fake_jpg), 'evidence.jpg', 'image/jpeg')
        }
        resp = self.client.post('/api/camera/capture', data=data, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 201)
        res = resp.get_json()
        self.assertTrue(res['success'])
        self.assertIn('snapshot_id', res)
        self.assertIn('file_hash', res)

        # Verify in DB
        snap = db.session.get(CameraSnapshot, res['snapshot_id'])
        self.assertIsNotNone(snap)
        self.assertEqual(snap.user_id, self.user.id)
        self.assertEqual(snap.device_id, self.cam_device.id)

    def test_camera_status_endpoint(self):
        """Camera telemetry status"""
        resp = self.client.get('/api/camera/status', headers=self.saheli_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['device_id'], 'SAHELI-CAM-001')
        self.assertEqual(data['camera_health'], 'HEALTHY')
        self.assertEqual(data['wifi_rssi'], -58)

    def test_snapshots_for_incident(self):
        """Retrieve evidence photos attached to an incident"""
        incident = EmergencyIncident(
            user_id=self.user.id,
            trigger_type='TOUCH',
            status='ACTIVE',
            latitude=28.6139,
            longitude=77.2090
        )
        db.session.add(incident)
        db.session.flush()

        snap = CameraSnapshot(
            incident_id=incident.id,
            device_id=self.cam_device.id,
            user_id=self.user.id,
            image_url='/uploads/camera/test1.jpg',
            file_size_bytes=1024,
            file_hash='abc123hash'
        )
        db.session.add(snap)
        db.session.commit()

        resp = self.client.get(f'/api/camera/snapshots/{incident.id}', headers=self.saheli_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['snapshots'][0]['file_hash'], 'abc123hash')

if __name__ == '__main__':
    unittest.main()
