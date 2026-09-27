import unittest
import numpy as np
from ai_ml.models.neuro_fuzzy import get_anfis_model
from ai_ml.models.genetic_route_optimizer import GeneticRouteOptimizer
from ai_ml.models.audio_anomaly_detector import get_audio_detector
from ai_ml.models.motion_anomaly_detector import get_motion_detector
from ai_ml.inference.predictor import inference_engine

class TestPhase7AIML(unittest.TestCase):

    def test_anfis_safe_conditions(self):
        """Test ANFIS outputs low risk for well-lit, crowded, daylight conditions"""
        anfis = get_anfis_model()
        res = anfis.predict_risk(
            lighting=0.95,
            crowd=0.90,
            police_dist_km=0.2,
            time_risk=0.10,
            crime_score=0.05,
            vulnerability=0.10
        )
        self.assertIn("risk_score", res)
        self.assertIn("safety_score", res)
        self.assertLess(res["risk_score"], 35.0)
        self.assertGreater(res["safety_score"], 65.0)
        self.assertIn(res["level"], ["VERY_SAFE", "LOW_RISK"])

    def test_anfis_danger_conditions(self):
        """Test ANFIS outputs high risk for dark, isolated, late night conditions"""
        anfis = get_anfis_model()
        res = anfis.predict_risk(
            lighting=0.05,
            crowd=0.05,
            police_dist_km=4.5,
            time_risk=0.95,
            crime_score=0.85,
            vulnerability=0.80
        )
        self.assertGreater(res["risk_score"], 60.0)
        self.assertIn(res["level"], ["HIGH_DANGER", "MODERATE_RISK"])

    def test_genetic_route_optimizer(self):
        """Test Genetic Algorithm produces safest, balanced, and fastest routes"""
        optimizer = GeneticRouteOptimizer(population_size=15, generations=10)
        origin = (28.6139, 77.2090) # Delhi India Gate
        dest = (28.6250, 77.2180)

        result = optimizer.generate_all_route_options(origin, dest, hour_of_day=22)
        self.assertIn("routes", result)
        self.assertIn("safest", result["routes"])
        self.assertIn("balanced", result["routes"])
        self.assertIn("fastest", result["routes"])

        safest = result["routes"]["safest"]
        self.assertGreater(len(safest["waypoints"]), 2)
        self.assertGreater(safest["distance_km"], 0.0)
        self.assertGreater(safest["safety_score"], 0.0)
        self.assertGreater(len(safest["steps"]), 0)

    def test_audio_screaming_detection(self):
        """Test acoustic classifier recognizes distress screaming features"""
        detector = get_audio_detector()
        # High frequency, high peak, high RMS simulated distress scream
        features = {
            "peak": 0.85,
            "rms": 0.35,
            "zcr": 0.15,
            "spectral_centroid": 3200.0
        }
        res = detector.classify_audio(features)
        self.assertEqual(res["classification"], "SCREAM_OR_SHOUT")
        self.assertTrue(res["is_emergency"])
        self.assertGreater(res["confidence"], 0.80)

    def test_motion_fall_detection(self):
        """Test IMU classifier recognizes high-impact fall"""
        detector = get_motion_detector()
        # 3.5g impact
        res = detector.evaluate_sample(ax=0.2, ay=3.4, az=0.8, gx=30.0, gy=20.0, gz=10.0)
        self.assertEqual(res["state"], "SUDDEN_FALL_IMPACT")
        self.assertTrue(res["is_fall"])
        self.assertTrue(res["is_emergency"])

    def test_motion_struggle_detection(self):
        """Test IMU classifier recognizes violent physical struggle"""
        detector = get_motion_detector()
        # High angular velocity
        res = detector.evaluate_sample(ax=1.0, ay=0.8, az=0.9, gx=180.0, gy=240.0, gz=90.0)
        self.assertEqual(res["state"], "PHYSICAL_STRUGGLE")
        self.assertTrue(res["is_struggle"])
        self.assertTrue(res["is_emergency"])

    def test_unified_inference_engine(self):
        """Test the unified inference engine facade"""
        risk = inference_engine.assess_risk(0.8, 0.7, 0.5, 0.2, 0.1)
        self.assertIn("risk_score", risk)

        motion = inference_engine.analyze_motion(0.1, 1.25, 0.1, 15.0, 10.0, 5.0)
        self.assertEqual(motion["state"], "NORMAL_WALKING")

if __name__ == '__main__':
    unittest.main()
