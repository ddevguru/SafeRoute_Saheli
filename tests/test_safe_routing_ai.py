import unittest
import torch
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.routing import RouteDeviation
from backend.app.auth.jwt_handler import create_access_token
from ai_ml.models.neuro_fuzzy import get_anfis_model, ANFISRiskModel
from ai_ml.models.genetic_route_optimizer import GeneticRouteOptimizer

class SafeRoutingAITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli user
        self.user = User(
            name="Meera Sen",
            email="meera@example.com",
            phone="+919876599999"
        )
        self.user.set_password("MeeraPass123!")
        db.session.add(self.user)
        db.session.commit()

        # JWT
        self.token = create_access_token(self.user.id, 'SAHELI', {'email': self.user.email})
        self.headers = {'Authorization': f"Bearer {self.token}"}

        self.anfis = get_anfis_model()
        self.ga_optimizer = GeneticRouteOptimizer(population_size=12, generations=8)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_neuro_fuzzy_anfis_safe_vs_dangerous(self):
        """ANFIS Neuro-Fuzzy distinguishes safe brightly-lit conditions from hazardous dark corridors"""
        safe_eval = self.anfis.predict_risk(
            lighting=0.95,
            crowd=0.85,
            police_dist_km=0.2,
            time_risk=0.1,
            crime_score=0.05,
            vulnerability=0.1
        )
        self.assertIn('risk_score', safe_eval)
        self.assertIn('safety_score', safe_eval)
        self.assertLess(safe_eval['risk_score'], 30.0)
        self.assertGreater(safe_eval['safety_score'], 70.0)

        danger_eval = self.anfis.predict_risk(
            lighting=0.10,
            crowd=0.05,
            police_dist_km=4.8,
            time_risk=0.95,
            crime_score=0.90,
            vulnerability=0.85
        )
        self.assertGreater(danger_eval['risk_score'], safe_eval['risk_score'])
        self.assertLess(danger_eval['safety_score'], safe_eval['safety_score'])

    def test_genetic_algorithm_multiobjective_routes(self):
        """Genetic algorithm generates 3 distinct optimized route options"""
        origin = (28.6139, 77.2090)
        dest = (28.6300, 77.2200)

        res = self.ga_optimizer.generate_all_route_options(origin, dest, hour_of_day=21)
        self.assertIn('routes', res)
        routes = res['routes']
        self.assertIn('safest', routes)
        self.assertIn('balanced', routes)
        self.assertIn('fastest', routes)

        for key in ['safest', 'balanced', 'fastest']:
            r = routes[key]
            self.assertGreater(len(r['waypoints']), 2)
            self.assertGreater(r['distance_km'], 0.0)
            self.assertGreater(r['safety_score'], 0.0)

    def test_api_routes_calculate(self):
        """POST /api/routes/calculate returns multi-route comparison"""
        payload = {
            'start_lat': 28.6139,
            'start_lng': 77.2090,
            'dest_lat': 28.6300,
            'dest_lng': 77.2200,
            'hour_of_day': 22
        }
        resp = self.client.post('/api/routes/calculate', json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['routes']), 3)

        types = [r['type'] for r in data['routes']]
        self.assertIn('SAFETY_OPTIMIZED', types)
        self.assertIn('BALANCED', types)
        self.assertIn('FASTEST', types)

    def test_api_routes_deviation_detection(self):
        """POST /api/routes/deviation flags deviation when user veers off course"""
        # Normal on-track: deviation 12 meters, threshold 50 meters
        payload_normal = {
            'route_id': 'route-safety-optimized',
            'latitude': 28.6140,
            'longitude': 77.2092,
            'threshold_meters': 50.0,
            'simulated_deviation_meters': 15.0
        }
        resp = self.client.post('/api/routes/deviation', json=payload_normal, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertFalse(data['is_deviated'])

        # Deviated off-track: deviation 120 meters, threshold 50 meters
        payload_deviated = {
            'route_id': 'route-safety-optimized',
            'latitude': 28.6180,
            'longitude': 77.2150,
            'threshold_meters': 50.0,
            'simulated_deviation_meters': 120.0
        }
        resp = self.client.post('/api/routes/deviation', json=payload_deviated, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_deviated'])
        self.assertEqual(data['action_required'], 'RECALCULATE')

        # Check DB log
        dev_records = RouteDeviation.query.filter_by(user_id=self.user.id).all()
        self.assertEqual(len(dev_records), 1)
        self.assertEqual(dev_records[0].deviation_distance_meters, 120.0)

if __name__ == '__main__':
    unittest.main()
