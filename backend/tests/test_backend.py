import unittest
import json
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import Guardian, GuardianUser

class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_health_endpoint(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'ONLINE')
        self.assertEqual(data['application'], 'SafeRoute Saheli')

    def test_user_registration_and_login(self):
        # Register
        reg_payload = {
            'name': 'Pooja Sharma',
            'email': 'pooja@example.com',
            'phone': '+919876543210',
            'password': 'SecureSaheliPass123!',
            'confirm_password': 'SecureSaheliPass123!',
            'emergency_blood_group': 'O+'
        }
        res = self.client.post('/api/auth/register', json=reg_payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('access_token', data)

        # Login
        login_payload = {
            'email': 'pooja@example.com',
            'password': 'SecureSaheliPass123!'
        }
        res_login = self.client.post('/api/auth/login', json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.get_json()
        self.assertTrue(login_data['success'])
        token = login_data['access_token']

        # Profile with Bearer Token
        res_prof = self.client.get('/api/auth/profile', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res_prof.status_code, 200)
        prof_data = res_prof.get_json()
        self.assertEqual(prof_data['user']['name'], 'Pooja Sharma')

    def test_guardian_flow(self):
        # Create Saheli
        saheli = User(name='Ananya', email='ananya@test.com', phone='+919811111111')
        saheli.set_password('Password123!')
        db.session.add(saheli)
        db.session.commit()

        # Login to get JWT
        res_login = self.client.post('/api/auth/login', json={'email': 'ananya@test.com', 'password': 'Password123!'})
        token = res_login.get_json()['access_token']

        # Add Guardian
        guardian_payload = {
            'name': 'Sunita (Mother)',
            'relationship': 'Mother',
            'phone': '+919822222222',
            'email': 'sunita@test.com',
            'username': 'sunita_mom',
            'password': 'GuardianPass@123',
            'can_view_location': True,
            'can_view_camera': True
        }
        res_g = self.client.post('/api/guardians', json=guardian_payload, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res_g.status_code, 201)
        g_data = res_g.get_json()
        self.assertTrue(g_data['success'])

        # Guardian login independently
        res_gl = self.client.post('/api/guardians/login', json={'username': 'sunita_mom', 'password': 'GuardianPass@123'})
        self.assertEqual(res_gl.status_code, 200)
        self.assertTrue(res_gl.get_json()['success'])

    def test_emergency_trigger_and_cancel(self):
        # Create Saheli
        saheli = User(name='Riya', email='riya@test.com', phone='+919833333333')
        saheli.set_password('Password123!')
        db.session.add(saheli)
        db.session.commit()

        res_login = self.client.post('/api/auth/login', json={'email': 'riya@test.com', 'password': 'Password123!'})
        token = res_login.get_json()['access_token']

        # Trigger Emergency
        trig_payload = {
            'trigger_type': 'TOUCH',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'battery_percent': 85
        }
        res_trig = self.client.post('/api/emergency/trigger', json=trig_payload, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res_trig.status_code, 200)
        trig_data = res_trig.get_json()
        self.assertTrue(trig_data['success'])
        incident_id = trig_data['incident_id']
        self.assertIn('tracking_url', trig_data)

        # Cancel Emergency
        res_cancel = self.client.post(f'/api/emergency/{incident_id}/cancel', json={'reason': 'Accidental tap verified'}, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res_cancel.status_code, 200)
        self.assertEqual(res_cancel.get_json()['status'], 'CANCELLED')

    def test_nearby_places(self):
        res = self.client.get('/api/nearby/police?lat=28.6139&lng=77.2090&radius_meters=5000')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 1)

    def test_neuro_fuzzy_risk_api(self):
        payload = {
            'crime_rate': 0.7,
            'lighting_quality': 0.2,
            'isolation_index': 0.8,
            'crowd_density': 0.1,
            'hour_of_day': 23
        }
        res = self.client.post('/api/ai/risk', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['evaluation']['risk_score'], 50.0)

if __name__ == '__main__':
    unittest.main()
