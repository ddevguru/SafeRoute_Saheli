import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models.routing import SafePlace
from backend.app.routes.nearby import haversine_distance

class NearbyServicesTestCase(unittest.TestCase):
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

    def test_haversine_formula_accuracy(self):
        """Haversine distance between New Delhi (28.6139, 77.2090) and Connaught Place (28.6315, 77.2167) ~2km"""
        dist = haversine_distance(28.6139, 77.2090, 28.6315, 77.2167)
        self.assertGreater(dist, 1800)
        self.assertLess(dist, 2300)

    def test_get_nearby_police_sorted(self):
        """GET /api/nearby/police returns verified police stations in order of distance"""
        resp = self.client.get('/api/nearby/police?lat=28.6139&lng=77.2090&radius_meters=5000')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        places = data['places']
        # Check ascending order
        distances = [p['distance_meters'] for p in places]
        self.assertEqual(distances, sorted(distances))
        self.assertEqual(places[0]['category'], 'POLICE')
        self.assertIsNotNone(places[0]['phone_number'])

    def test_get_nearby_hospitals(self):
        """GET /api/nearby/hospitals returns emergency hospitals"""
        resp = self.client.get('/api/nearby/hospitals?lat=28.6139&lng=77.2090&radius_meters=5000')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        self.assertEqual(data['places'][0]['category'], 'HOSPITAL')
        self.assertTrue(data['places'][0]['is_24x7'])

    def test_get_nearby_safe_places_with_filter(self):
        """GET /api/nearby/safe-places with category filter"""
        resp = self.client.get('/api/nearby/safe-places?category=SHELTER')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        for p in data['places']:
            self.assertEqual(p['category'], 'SHELTER')

    def test_get_all_categorized_emergency_services(self):
        """GET /api/nearby/all aggregates all categories with summary counts"""
        resp = self.client.get('/api/nearby/all?lat=28.6139&lng=77.2090&radius_meters=10000')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('summary', data)
        self.assertIn('places', data)
        self.assertGreaterEqual(data['summary']['police_count'], 1)
        self.assertGreaterEqual(data['summary']['hospital_count'], 1)
        self.assertGreaterEqual(data['summary']['shelter_count'], 1)
        self.assertIn('police', data['places'])
        self.assertIn('hospitals', data['places'])
        self.assertIn('shelters', data['places'])

if __name__ == '__main__':
    unittest.main()
