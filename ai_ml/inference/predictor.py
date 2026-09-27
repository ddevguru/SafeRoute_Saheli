"""
SafeRoute Saheli — Unified AI/ML Inference Pipeline
Provides simplified, thread-safe inference APIs for Backend Services and REST Endpoints.
"""

from typing import Dict, Any, Tuple
from ai_ml.models.neuro_fuzzy import get_anfis_model
from ai_ml.models.genetic_route_optimizer import GeneticRouteOptimizer
from ai_ml.models.audio_anomaly_detector import get_audio_detector
from ai_ml.models.motion_anomaly_detector import get_motion_detector

class SafetyInferenceEngine:
    """
    Facade exposing AI and Soft Computing models to Flask routes and WebSocket handlers.
    """
    def __init__(self):
        self.anfis = get_anfis_model()
        self.route_optimizer = GeneticRouteOptimizer()
        self.audio_detector = get_audio_detector()
        self.motion_detector = get_motion_detector()

    def assess_risk(self, lighting: float, crowd: float, police_dist_km: float,
                    time_risk: float, crime_score: float, vulnerability: float = 0.5) -> Dict[str, Any]:
        """Assess location safety using ANFIS Neuro-Fuzzy model"""
        return self.anfis.predict_risk(
            lighting=lighting,
            crowd=crowd,
            police_dist_km=police_dist_km,
            time_risk=time_risk,
            crime_score=crime_score,
            vulnerability=vulnerability
        )

    def plan_safe_route(self, origin: Tuple[float, float], dest: Tuple[float, float],
                        hour_of_day: int = 21) -> Dict[str, Any]:
        """Generate safe, balanced, and fast routing options using Genetic Algorithm"""
        return self.route_optimizer.generate_all_route_options(origin, dest, hour_of_day)

    def analyze_audio(self, signal_or_features: Any) -> Dict[str, Any]:
        """Detect distress keywords or screaming in audio sample"""
        return self.audio_detector.classify_audio(signal_or_features)

    def analyze_motion(self, ax: float, ay: float, az: float,
                       gx: float, gy: float, gz: float) -> Dict[str, Any]:
        """Detect falls or struggle motion from 6-axis IMU"""
        return self.motion_detector.evaluate_sample(ax, ay, az, gx, gy, gz)


# Singleton
inference_engine = SafetyInferenceEngine()
