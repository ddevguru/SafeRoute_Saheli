"""
SafeRoute Saheli — Biometric Stress & Acute Panic Anomaly Detector
Analyzes photoplethysmography (PPG) telemetry from MAX30102 sensor:
Heart Rate (BPM), SpO2, Heart Rate Variability (RMSSD), and cross-references
with 3-axis motion to differentiate exercise tachycardia from acute panic distress.
"""

import math
from typing import Dict, Any, List, Optional


class BiometricStressDetector:
    """
    Evaluates cardiovascular and autonomic nervous system stress indicators
    for silent panic, fear-induced tachycardia, and physiological distress.
    """

    def __init__(
        self,
        default_baseline_bpm: float = 75.0,
        panic_bpm_threshold: float = 130.0,
        stress_bpm_threshold: float = 105.0,
        min_safe_spo2: float = 90.0,
    ):
        self.default_baseline_bpm = default_baseline_bpm
        self.panic_bpm_threshold = panic_bpm_threshold
        self.stress_bpm_threshold = stress_bpm_threshold
        self.min_safe_spo2 = min_safe_spo2

    def calculate_rmssd(self, rr_intervals_ms: Optional[List[float]]) -> Optional[float]:
        """
        Calculates Root Mean Square of Successive Differences (RMSSD) from RR-intervals.
        Low RMSSD (<20ms) correlates with acute sympathetic activation (panic).
        """
        if not rr_intervals_ms or len(rr_intervals_ms) < 3:
            return None

        diffs = [
            (rr_intervals_ms[i + 1] - rr_intervals_ms[i]) ** 2
            for i in range(len(rr_intervals_ms) - 1)
        ]
        mean_diff = sum(diffs) / len(diffs)
        return round(math.sqrt(mean_diff), 2)

    def evaluate_biometrics(
        self,
        bpm: float,
        spo2: float,
        accel_mag_g: float = 1.0,
        user_baseline_bpm: Optional[float] = None,
        rr_intervals_ms: Optional[List[float]] = None,
        is_finger_detected: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluate biometric telemetry and classify physiological stress state.

        :param bpm: Measured Heart Rate in Beats Per Minute
        :param spo2: Blood oxygen saturation percentage (0-100%)
        :param accel_mag_g: Magnitude of 3-axis acceleration (default 1.0g = at rest)
        :param user_baseline_bpm: User's calibrated resting heart rate
        :param rr_intervals_ms: Optional recent RR intervals in milliseconds
        :param is_finger_detected: Whether sensor has solid skin contact
        :return: Assessment dict with stress_score (0-100), state, and emergency flags
        """
        if not is_finger_detected or bpm <= 20.0 or spo2 <= 40.0:
            return {
                "state": "SENSOR_DISCONNECTED",
                "is_panic_emergency": False,
                "is_hypoxia_emergency": False,
                "is_emergency": False,
                "stress_score": 0.0,
                "confidence": 0.99,
                "interpretation": "Wearable sensor not in contact with skin",
                "metrics": {
                    "bpm": round(bpm, 1),
                    "spo2": round(spo2, 1),
                    "accel_mag_g": round(accel_mag_g, 2),
                    "rmssd_ms": None,
                },
            }

        baseline = user_baseline_bpm if user_baseline_bpm and user_baseline_bpm > 45 else self.default_baseline_bpm
        rmssd = self.calculate_rmssd(rr_intervals_ms)

        # Baseline deviation
        bpm_delta = bpm - baseline

        # Cross-reference with motion:
        # High physical motion (>1.6g) suggests running or sports (exercise tachycardia)
        is_high_motion = accel_mag_g >= 1.55

        # Hypoxia check
        is_hypoxia = spo2 < self.min_safe_spo2

        # Stress calculation logic
        # 1. Base score from BPM elevation above baseline
        if bpm <= baseline:
            base_score = max(0.0, (bpm / baseline) * 20.0)
        else:
            # Scale difference above baseline up to 100
            base_score = 20.0 + min(80.0, (bpm_delta / 60.0) * 80.0)

        # 2. Adjust if low HRV (sympathetic surge)
        if rmssd is not None:
            if rmssd < 20.0:  # Acute stress / fight or flight
                base_score = min(100.0, base_score + 15.0)
            elif rmssd > 50.0:  # High parasympathetic tone (calm)
                base_score = max(0.0, base_score - 10.0)

        # 3. Classify Panic vs Exercise:
        # If HR is acutely high (>125 BPM or delta > 40) BUT person is physically still,
        # it is a strong physiological signature of severe fright or silent assault.
        is_acute_panic = False
        state = "CALM"
        confidence = 0.90

        if is_hypoxia:
            state = "CRITICAL_HYPOXIA"
            confidence = 0.95
        elif bpm >= self.panic_bpm_threshold and not is_high_motion:
            # Tachycardia without exertion = Acute Panic
            state = "ACUTE_PANIC_TACHYCARDIA"
            is_acute_panic = True
            base_score = max(base_score, 88.0)
            confidence = 0.94
        elif bpm >= self.panic_bpm_threshold and is_high_motion:
            # Tachycardia with high motion = Running / Exercise
            state = "EXERTION_TACHYCARDIA"
            base_score = min(base_score, 65.0)
            confidence = 0.88
        elif bpm_delta >= 40.0 and not is_high_motion and bpm >= 115.0:
            state = "ACUTE_PANIC_SURGE"
            is_acute_panic = True
            base_score = max(base_score, 82.0)
            confidence = 0.91
        elif bpm >= self.stress_bpm_threshold:
            state = "ELEVATED_STRESS"
            confidence = 0.89
        elif bpm >= baseline + 10.0:
            state = "MODERATE_ALERT"
            confidence = 0.92
        else:
            state = "CALM"
            confidence = 0.95

        stress_score = round(max(0.0, min(100.0, base_score)), 1)
        is_emergency = is_acute_panic or is_hypoxia

        interpretation_map = {
            "CRITICAL_HYPOXIA": "Dangerous blood oxygen desaturation (<90%). Immediate medical attention advised.",
            "ACUTE_PANIC_TACHYCARDIA": "Severe heart rate spike (>130 BPM) detected without physical exertion. Silent panic or acute danger likely.",
            "ACUTE_PANIC_SURGE": "Rapid abnormal heart rate surge (+40 BPM above baseline) while stationary. Possible threat or fear response.",
            "EXERTION_TACHYCARDIA": "Elevated heart rate accompanied by active movement (running/exercise).",
            "ELEVATED_STRESS": "Heightened heart rate detected. Physiological stress or nervousness.",
            "MODERATE_ALERT": "Slightly elevated cardiovascular parameters within tolerable threshold.",
            "CALM": "Cardiovascular metrics within normal resting baseline range.",
        }

        return {
            "state": state,
            "is_panic_emergency": is_acute_panic,
            "is_hypoxia_emergency": is_hypoxia,
            "is_emergency": is_emergency,
            "stress_score": stress_score,
            "confidence": round(confidence, 2),
            "interpretation": interpretation_map.get(state, "Biometric evaluation complete."),
            "metrics": {
                "bpm": round(bpm, 1),
                "spo2": round(spo2, 1),
                "baseline_bpm": round(baseline, 1),
                "bpm_delta": round(bpm_delta, 1),
                "accel_mag_g": round(accel_mag_g, 2),
                "rmssd_ms": rmssd,
            },
        }


# Singleton instance
_biometric_detector: Optional[BiometricStressDetector] = None


def get_biometric_detector() -> BiometricStressDetector:
    global _biometric_detector
    if _biometric_detector is None:
        _biometric_detector = BiometricStressDetector()
    return _biometric_detector
