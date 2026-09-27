"""
SafeRoute Saheli — Multi-Modal Soft Computing Sensor Fusion Engine
Performs real-time Bayesian State Estimation fusing 5 concurrent sensory modalities:
1. Capacitive Touch (TTP223 continuous hold)
2. 6-Axis Motion / IMU (MPU6050 fall, tumble, struggle)
3. Acoustic Telemetry (INMP441 scream, clap, keyword spotting)
4. PPG Biometrics (MAX30102 tachycardia, HRV collapse, hypoxia)
5. ANFIS Geo-Temporal Environmental Vulnerability

Computes Bayesian Posterior Threat Probability P(Threat | Sensors) to trigger
autonomous multi-tier alarms even when no individual threshold alone is breached.
"""

import math
from typing import Dict, Any, List, Optional


class MultiModalSensorFusionEngine:
    """
    Bayesian multi-modal threat state estimator for women's safety wearables.
    """

    def __init__(
        self,
        base_prior_assault: float = 0.015,
        emergency_decision_threshold: float = 0.75,
        elevated_alert_threshold: float = 0.50,
    ):
        self.base_prior = base_prior_assault
        self.emergency_threshold = emergency_decision_threshold
        self.elevated_threshold = elevated_alert_threshold

    def _safe_prob(self, p: float) -> float:
        """Clamp probability away from 0.0 and 1.0 to prevent division by zero"""
        return max(0.0001, min(0.9999, p))

    def compute_touch_likelihoods(self, touch_hold_duration_ms: float) -> tuple[float, float]:
        """Returns (P(Touch | Threat), P(Touch | Safe))"""
        if touch_hold_duration_ms >= 1500.0:
            return (0.98, 0.005)
        elif touch_hold_duration_ms >= 800.0:
            return (0.75, 0.05)
        elif touch_hold_duration_ms >= 200.0:
            return (0.45, 0.20)
        # In a violent assault, the victim may be pinned or knocked down (neutral evidence, not safe proof)
        return (0.45, 0.55)

    def compute_motion_likelihoods(
        self, is_fall: bool, is_struggle: bool, accel_mag_g: float
    ) -> tuple[float, float]:
        """Returns (P(Motion | Threat), P(Motion | Safe))"""
        if is_fall and is_struggle:
            return (0.98, 0.005)
        elif is_fall or accel_mag_g >= 2.8:
            return (0.88, 0.02)
        elif is_struggle:
            return (0.88, 0.03)
        elif accel_mag_g >= 1.6:  # running / fleeing
            return (0.50, 0.20)
        return (0.10, 0.90)

    def compute_audio_likelihoods(
        self, is_scream: bool, is_keyword: bool, is_clap: bool, confidence: float
    ) -> tuple[float, float]:
        """Returns (P(Audio | Threat), P(Audio | Safe))"""
        if is_keyword or (is_scream and confidence > 0.85):
            return (0.96, 0.01)
        elif is_clap:
            return (0.92, 0.02)
        elif is_scream:
            return (0.88, 0.03)
        return (0.08, 0.92)

    def compute_biometric_likelihoods(
        self, is_tachycardia_panic: bool, stress_score: float, is_hypoxia: bool
    ) -> tuple[float, float]:
        """Returns (P(Biometrics | Threat), P(Biometrics | Safe))"""
        if is_tachycardia_panic and stress_score >= 80.0:
            return (0.95, 0.015)
        elif is_hypoxia:
            return (0.88, 0.03)
        elif stress_score >= 60.0:
            return (0.68, 0.10)
        elif stress_score >= 40.0:
            return (0.35, 0.35)
        return (0.05, 0.95)

    def fuse_telemetry(
        self,
        # 1. Capacitive Touch
        touch_hold_ms: float = 0.0,
        # 2. Motion / IMU
        accel_mag_g: float = 1.0,
        gyro_mag_dps: float = 0.0,
        is_fall: bool = False,
        is_struggle: bool = False,
        # 3. Acoustic
        is_scream: bool = False,
        is_keyword: bool = False,
        is_clap: bool = False,
        audio_confidence: float = 0.0,
        # 4. Biometrics
        heart_rate_bpm: float = 75.0,
        spo2: float = 98.0,
        stress_score: float = 10.0,
        is_panic_tachycardia: bool = False,
        is_hypoxia: bool = False,
        # 5. Geo-Temporal Risk (ANFIS 0-100)
        anfis_risk_score: float = 25.0,
        hour_of_day: int = 14,
    ) -> Dict[str, Any]:
        """
        Executes multi-modal Bayesian posterior fusion across all available sensor streams.
        """
        # Dynamic prior modulated by environmental & diurnal risk:
        # Late night (22:00 to 05:00) + high crime/unlit area increases prior vulnerability
        is_night = (hour_of_day >= 22 or hour_of_day <= 5)
        night_multiplier = 1.8 if is_night else 1.0
        env_multiplier = 1.0 + (anfis_risk_score / 100.0) * 1.5

        prior_threat = min(0.15, self.base_prior * night_multiplier * env_multiplier)
        prior_safe = 1.0 - prior_threat

        # Compute likelihoods for each modality
        p_touch_t, p_touch_s = self.compute_touch_likelihoods(touch_hold_ms)
        p_motion_t, p_motion_s = self.compute_motion_likelihoods(is_fall, is_struggle, accel_mag_g)
        p_audio_t, p_audio_s = self.compute_audio_likelihoods(
            is_scream, is_keyword, is_clap, audio_confidence
        )
        p_bio_t, p_bio_s = self.compute_biometric_likelihoods(
            is_panic_tachycardia, stress_score, is_hypoxia
        )

        # Bayesian numerator and denominator:
        threat_evidence_prod = (
            self._safe_prob(p_touch_t)
            * self._safe_prob(p_motion_t)
            * self._safe_prob(p_audio_t)
            * self._safe_prob(p_bio_t)
        )

        safe_evidence_prod = (
            self._safe_prob(p_touch_s)
            * self._safe_prob(p_motion_s)
            * self._safe_prob(p_audio_s)
            * self._safe_prob(p_bio_s)
        )

        num = prior_threat * threat_evidence_prod
        den = num + (prior_safe * safe_evidence_prod)
        posterior = num / den if den > 0 else prior_threat

        # Hard manual trigger override: continuous touch >= 1500ms is an explicit user declaration
        if touch_hold_ms >= 1500.0:
            posterior = max(posterior, 0.99)

        # Multiple coincident signals synergy:
        coincident_signals = sum([
            1 if touch_hold_ms >= 800.0 else 0,
            1 if is_fall else 0,
            1 if is_struggle else 0,
            1 if (is_scream or is_keyword or is_clap) else 0,
            1 if (is_panic_tachycardia or heart_rate_bpm >= 120.0) else 0,
            1 if anfis_risk_score >= 60.0 else 0,
        ])

        if coincident_signals >= 3:
            posterior = max(posterior, 0.92)
        elif coincident_signals >= 2 and posterior < 0.70:
            posterior = max(posterior, 0.80)

        posterior = round(min(0.999, max(0.001, posterior)), 3)

        # Classification & Actions
        contributing_factors = []
        if touch_hold_ms >= 800.0:
            contributing_factors.append(f"TOUCH_HOLD_{int(touch_hold_ms)}MS")
        if is_fall:
            contributing_factors.append("FALL_IMPACT_DETECTED")
        if is_struggle:
            contributing_factors.append("PHYSICAL_STRUGGLE_DETECTED")
        if is_keyword:
            contributing_factors.append("DISTRESS_KEYWORD_DETECTED")
        if is_scream:
            contributing_factors.append("SCREAM_ACOUSTIC_DETECTED")
        if is_clap:
            contributing_factors.append("TRIPLE_CLAP_DETECTED")
        if is_panic_tachycardia:
            contributing_factors.append(f"ACUTE_PANIC_TACHYCARDIA_{int(heart_rate_bpm)}BPM")
        if is_hypoxia:
            contributing_factors.append(f"CRITICAL_HYPOXIA_{int(spo2)}PCT")
        if anfis_risk_score >= 65.0:
            contributing_factors.append(f"HIGH_VULNERABILITY_ZONE_{int(anfis_risk_score)}PTS")

        if posterior >= self.emergency_threshold:
            threat_level = "CRITICAL_EMERGENCY"
            action = "FULL_POLICE_GUARDIAN_DISPATCH"
            is_emergency = True
        elif posterior >= self.elevated_threshold:
            threat_level = "ELEVATED_THREAT"
            action = "AUDIO_CAMERA_BURST_AND_NOTIFY"
            is_emergency = False
        elif posterior >= 0.20:
            threat_level = "GUARDED"
            action = "INCREASE_GPS_SAMPLING_FREQUENCY"
            is_emergency = False
        else:
            threat_level = "NORMAL_SECURE"
            action = "STANDARD_MONITORING"
            is_emergency = False

        confidence = round(min(0.99, 0.70 + (coincident_signals * 0.08)), 2)

        return {
            "threat_probability": posterior,
            "threat_percentage": round(posterior * 100.0, 1),
            "threat_level": threat_level,
            "is_emergency_triggered": is_emergency,
            "coincident_signal_count": coincident_signals,
            "contributing_factors": contributing_factors,
            "recommended_action": action,
            "confidence": confidence,
            "sensor_summary": {
                "touch_ms": touch_hold_ms,
                "accel_mag_g": round(accel_mag_g, 2),
                "bpm": round(heart_rate_bpm, 1),
                "spo2": round(spo2, 1),
                "anfis_risk": round(anfis_risk_score, 1),
                "is_night": is_night,
            },
        }


# Singleton instance
_fusion_engine: Optional[MultiModalSensorFusionEngine] = None


def get_sensor_fusion_engine() -> MultiModalSensorFusionEngine:
    global _fusion_engine
    if _fusion_engine is None:
        _fusion_engine = MultiModalSensorFusionEngine()
    return _fusion_engine
