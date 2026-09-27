import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.routing import SafePlace
from backend.app.auth.jwt_handler import create_access_token

class TestPhase8Routes(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Create test Saheli user
        self.user = User(
            name="Pooja Sharma",
            email="pooja.routes@example.com",
            phone="+919876543222"
        )
        self.user.set_password("SecurePass123!")
        db.session.add(self.user)

        # Seed safe places
        p1 = SafePlace(
            name="Connaught Place Police Station",
            category="POLICE",
            latitude=28.6310,
            longitude=77.2180,
            address="Connaught Place, New Delhi",
            phone_number="+911123412345",
            verified_status=True
        )
        p2 = SafePlace(
            name="Ram Manohar Lohia Hospital",
            category="HOSPITAL",
            latitude=28.6250,
            longitude=77.2020,
            address="Baba Kharak Singh Marg, New Delhi",
            phone_number="+911123365525",
            verified_status=True
        )
        db.session.add_all([p1, p2])
        db.session.commit()

        token = create_access_token(identity=str(self.user.id), role='SAHELI')
        self.headers = {'Authorization': f"Bearer {token}"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_calculate_routes_genetic_algorithm(self):
        """Verify Genetic Algorithm Safe Route generation endpoint"""
        payload = {
            "start_lat": 28.6139,
            "start_lng": 77.2090,
            "dest_lat": 28.6300,
            "dest_lng": 77.2200,
            "hour_of_day": 22
        }
        res = self.client.post('/api/routes/calculate', json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['routes']), 3)

        safe_route = next(r for r in data['routes'] if r['type'] == 'SAFETY_OPTIMIZED')
        self.assertGreater(safe_route['safety_score'], 0.0)
        self.assertGreater(safe_route['distance_km'], 0.0)
        self.assertGreater(len(safe_route['coordinates']), 2)

    def test_check_route_deviation(self):
        """Verify route deviation alert recording"""
        payload = {
            "route_id": "test-route-1",
            "latitude": 28.6150,
            "longitude": 77.2100,
            "threshold_meters": 50.0,
            "simulated_deviation_meters": 85.0
        }
        res = self.client.post('/api/routes/deviation', json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_deviated'])
        self.assertEqual(data['action_required'], 'RECALCULATE')

    def test_nearby_safe_places(self):
        """Verify retrieval of nearby police stations and safe havens"""
        res = self.client.get('/api/nearby/police?lat=28.6139&lng=77.2090&radius_meters=5000')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 1)
        self.assertEqual(data['places'][0]['category'], 'POLICE')

    def test_ai_risk_endpoint(self):
        """Verify AI risk evaluation endpoint"""
        payload = {
            "crime_rate": 0.8,
            "lighting_quality": 0.2,
            "isolation_index": 0.9,
            "crowd_density": 0.1,
            "hour_of_day": 2
        }
        res = self.client.post('/api/ai/risk', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['evaluation']['risk_score'], 50.0)

if __name__ == '__main__':
    unittest.main()
