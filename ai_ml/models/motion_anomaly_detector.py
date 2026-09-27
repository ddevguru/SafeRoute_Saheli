"""
SafeRoute Saheli — 6-Axis Motion Anomaly Classifier
Detects sudden falls, physical struggles, running, and stationary states from MPU6050 telemetry.
"""

import math
from typing import Dict, Any, List

class MotionAnomalyDetector:
    """
    Evaluates accelerometer and gyroscope vectors for physical assault or fall patterns
    """
    def __init__(self, fall_threshold_g: float = 2.8, struggle_threshold_dps: float = 200.0):
        self.fall_threshold = fall_threshold_g
        self.struggle_threshold = struggle_threshold_dps

    def evaluate_sample(self, ax: float, ay: float, az: float,
                        gx: float, gy: float, gz: float) -> Dict[str, Any]:
        """
        Evaluate a single 6-axis IMU reading
        ax, ay, az: acceleration in g
        gx, gy, gz: angular velocity in degrees per second (dps)
        """
        accel_mag = math.sqrt(ax * ax + ay * ay + az * az)
        gyro_mag = math.sqrt(gx * gx + gy * gy + gz * gz)

        is_fall = False
        is_struggle = False
        state = "STATIONARY"
        confidence = 0.90

        if accel_mag > self.fall_threshold:
            state = "SUDDEN_FALL_IMPACT"
            is_fall = True
            confidence = min(0.98, 0.70 + (accel_mag / 4.0) * 0.28)
        elif gyro_mag > self.struggle_threshold:
            state = "PHYSICAL_STRUGGLE"
            is_struggle = True
            confidence = min(0.95, 0.65 + (gyro_mag / 350.0) * 0.30)
        elif accel_mag > 1.6:
            state = "RUNNING_FAST"
            confidence = 0.88
        elif accel_mag > 1.15:
            state = "NORMAL_WALKING"
            confidence = 0.92
        else:
            state = "STATIONARY"
            confidence = 0.95

        return {
            "state": state,
            "is_emergency": is_fall or is_struggle,
            "is_fall": is_fall,
            "is_struggle": is_struggle,
            "confidence": round(confidence, 2),
            "metrics": {
                "accel_magnitude_g": round(accel_mag, 2),
                "gyro_magnitude_dps": round(gyro_mag, 2)
            }
        }


# Singleton instance
_motion_detector = None

def get_motion_detector() -> MotionAnomalyDetector:
    global _motion_detector
    if _motion_detector is None:
        _motion_detector = MotionAnomalyDetector()
    return _motion_detector
