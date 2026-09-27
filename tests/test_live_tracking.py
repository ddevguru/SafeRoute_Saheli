import unittest
from datetime import datetime, timedelta
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident, LiveTrackingSession, TrackingToken
from backend.app.models.location import LocationHistory
from backend.app.auth.jwt_handler import create_access_token

class LiveTrackingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli user
        self.user = User(
            name="Rupali Sharma",
            email="rupali@example.com",
            phone="+919876543210"
        )
        self.user.set_password("SecurePass123!")
        db.session.add(self.user)

        # Seed Guardian
        self.guardian = Guardian(
            name="Anita Sharma",
            username="anita_sharma",
            email="anita@example.com",
            phone="+919876543211",
            relationship="MOTHER"
        )
        self.guardian.set_password("MotherPass123!")
        db.session.add(self.guardian)
        db.session.commit()

        # Link Guardian with permissions
        self.link = GuardianUser(
            saheli_id=self.user.id,
            guardian_id=self.guardian.id,
            relationship_label="MOTHER",
            can_view_location=True,
            can_view_camera=True
        )
        db.session.add(self.link)

        # Register ESP32 Wearable Device
        self.device = Device(
            device_id="SAHELI-WEARABLE-001",
            device_type="WEARABLE_ESP32",
            assigned_user_id=self.user.id,
            battery_percent=92
        )
        self.device.set_secret("esp32_secret_key_2026")
        db.session.add(self.device)
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

    def test_location_update_via_jwt(self):
        """Saheli mobile app pushing GPS coordinates"""
        payload = {
            'latitude': 28.6139,
            'longitude': 77.2090,
            'accuracy': 4.5,
            'speed': 1.2,
            'heading': 90.0,
            'battery': 88
        }
        resp = self.client.post('/api/location/update', json=payload, headers=self.saheli_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])

        # Verify record in LocationHistory
        loc = LocationHistory.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(loc)
        self.assertAlmostEqual(float(loc.latitude), 28.6139)
        self.assertFalse(loc.is_emergency)

    def test_location_update_via_device_secret(self):
        """ESP32 hardware pushing GPS coordinates with hardware credentials"""
        payload = {
            'device_id': 'SAHELI-WEARABLE-001',
            'device_secret': 'esp32_secret_key_2026',
            'latitude': 28.6145,
            'longitude': 77.2095,
            'accuracy': 3.0,
            'speed': 0.0,
            'battery': 85
        }
        resp = self.client.post('/api/location/update', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])

        loc = LocationHistory.query.filter_by(device_id='SAHELI-WEARABLE-001').first()
        self.assertIsNotNone(loc)
        self.assertEqual(loc.user_id, self.user.id)

    def test_guardian_fetch_current_location(self):
        """Guardian with permission reading Saheli location"""
        loc = LocationHistory(
            user_id=self.user.id,
            latitude=28.6150,
            longitude=77.2100,
            accuracy=5.0,
            battery_level=90
        )
        db.session.add(loc)
        db.session.commit()

        resp = self.client.get(f'/api/location/current/{self.user.id}', headers=self.guardian_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertAlmostEqual(data['location']['latitude'], 28.6150)

    def test_location_history_trail(self):
        """Fetch chronological location trail points"""
        for i in range(5):
            loc = LocationHistory(
                user_id=self.user.id,
                latitude=28.6130 + (i * 0.001),
                longitude=77.2080 + (i * 0.001),
                accuracy=5.0,
                battery_level=90 - i
            )
            db.session.add(loc)
        db.session.commit()

        resp = self.client.get(f'/api/location/history/{self.user.id}?limit=10', headers=self.guardian_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 5)
        self.assertEqual(len(data['history']), 5)

    def test_public_live_tracking_page_and_api(self):
        """Tokenized public tracking page for emergency contacts without app"""
        # Create active incident and session
        incident = EmergencyIncident(
            user_id=self.user.id,
            trigger_type='TOUCH',
            status='ACTIVE',
            latitude=28.6139,
            longitude=77.2090,
            battery_percent=80
        )
        db.session.add(incident)
        db.session.flush()

        token_str = "safe_tracking_test_token_12345"
        session = LiveTrackingSession(
            incident_id=incident.id,
            user_id=self.user.id,
            tracking_token=token_str,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(hours=6)
        )
        db.session.add(session)
        db.session.flush()

        token_record = TrackingToken(
            session_id=session.id,
            token_value=token_str,
            expires_at=session.expires_at
        )
        db.session.add(token_record)

        loc = LocationHistory(
            user_id=self.user.id,
            incident_id=incident.id,
            latitude=28.6139,
            longitude=77.2090,
            accuracy=4.0,
            battery_level=80,
            is_emergency=True
        )
        db.session.add(loc)
        db.session.commit()

        # 1. HTML tracking page view
        page_resp = self.client.get(f'/track/{token_str}')
        self.assertEqual(page_resp.status_code, 200)
        html = page_resp.get_data(as_text=True)
        self.assertIn("SafeRoute Saheli", html)
        self.assertIn("Rupali Sharma", html)
        self.assertIn("EMERGENCY ACTIVE", html)
        self.assertIn("Call Police (112)", html)

        # 2. JSON tracking polling API
        api_resp = self.client.get(f'/track/{token_str}/api')
        self.assertEqual(api_resp.status_code, 200)
        api_data = api_resp.get_json()
        self.assertTrue(api_data['success'])
        self.assertEqual(api_data['incident']['status'], 'ACTIVE')
        self.assertEqual(api_data['user']['name'], 'Rupali Sharma')
        self.assertAlmostEqual(api_data['current_location']['latitude'], 28.6139)
        self.assertEqual(len(api_data['breadcrumb']), 1)

if __name__ == '__main__':
    unittest.main()
