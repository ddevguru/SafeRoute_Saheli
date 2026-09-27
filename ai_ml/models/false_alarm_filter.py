"""
SafeRoute Saheli — AI Real-Time False Alarm Suppression & Smart Cancel Watchdog
Evaluates post-trigger multi-modal telemetry (15-second grace window):
1. Rhythmic gait regularity vs violent struggle/recumbent immobility.
2. Biometric heart rate recovery vs persistent acute panic tachycardia.
3. Vernacular speech transcript analysis (cancellation intent vs duress coercion cues).
4. Dual-PIN security authentication (Normal Cancel PIN vs Covert Duress PIN).
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class FalseAlarmFilter:
    """
    AI Real-Time False Alarm Suppression & Smart Cancel Watchdog.
    Suppresses alert fatigue while guaranteeing zero compromise on victim safety
    by detecting attacker coercion via Covert Duress PINs and verbal distress indicators.
    """

    DEFAULT_GRACE_WINDOW_SECONDS = 15.0
    UNIVERSAL_DURESS_PINS = {"9999", "0000", "9111"}

    # Verbal cancellation keywords in English, Hindi, and Hinglish
    CANCEL_KEYWORDS = [
        "false alarm", "galti se", "cancel", "i am safe", "im safe", "safe",
        "theek hoon", "thik hu", "sab theek", "accidental", "mistake",
        "dab gaya", "press ho gaya", "sorry", "all good", "koi problem nahi",
        "disarm", "dont worry", "mai theek hu", "main theek hoon"
    ]

    # Duress / coercion cue keywords
    DURESS_KEYWORDS = [
        "dont hurt me", "don't hurt me", "chhod do", "chhor do", "chhod mujhe",
        "let me go", "leave me", "maar mat", "paise lelo", "nahi bolungi",
        "code red", "duress", "force", "please stop", "darr lag raha", "mat maro"
    ]

    def __init__(self, grace_window_seconds: float = DEFAULT_GRACE_WINDOW_SECONDS):
        self.grace_window_seconds = grace_window_seconds

    def evaluate_gait_regularity(self, motion_samples: Optional[List[Any]]) -> Dict[str, Any]:
        """
        Evaluates accelerometer & gyroscope stream over the post-trigger window.
        Distinguishes between:
        - Regular rhythmic walking / standing (high false alarm probability)
        - Violent struggle / tumbling (imminent threat)
        - Recumbent immobility post-impact (unconscious fall victim)
        """
        if not motion_samples:
            return {
                "stability_score": 0.50,
                "motion_state": "UNKNOWN",
                "is_struggle": False,
                "is_fall_shock": False,
                "details": "No motion telemetry provided"
            }

        # Extract acceleration magnitudes
        mags = []
        gyros = []
        for sample in motion_samples:
            if isinstance(sample, (int, float)):
                mags.append(float(sample))
            elif isinstance(sample, dict):
                if 'accel_mag' in sample:
                    mags.append(float(sample['accel_mag']))
                elif 'ax' in sample and 'ay' in sample and 'az' in sample:
                    ax, ay, az = float(sample['ax']), float(sample['ay']), float(sample['az'])
                    mags.append(math.sqrt(ax * ax + ay * ay + az * az))
                if 'gyro_mag' in sample:
                    gyros.append(float(sample['gyro_mag']))
                elif 'gx' in sample and 'gy' in sample and 'gz' in sample:
                    gx, gy, gz = float(sample['gx']), float(sample['gy']), float(sample['gz'])
                    gyros.append(math.sqrt(gx * gx + gy * gy + gz * gz))

        if not mags:
            return {
                "stability_score": 0.50,
                "motion_state": "UNKNOWN",
                "is_struggle": False,
                "is_fall_shock": False,
                "details": "Empty sample buffer"
            }

        n = len(mags)
        mean_mag = sum(mags) / n
        variance = sum((m - mean_mag) ** 2 for m in mags) / n if n > 1 else 0.0
        std_dev = math.sqrt(variance)
        max_mag = max(mags)
        max_gyro = max(gyros) if gyros else 0.0

        is_fall_shock = max_mag > 2.8
        is_struggle = max_gyro > 200.0 or variance > 0.85

        # Classification logic
        if is_fall_shock or is_struggle:
            motion_state = "VIOLENT_STRUGGLE_OR_FALL"
            stability_score = 0.05
        elif std_dev < 0.02 and mean_mag < 0.4:
            # Low gravity orientation flat on ground with no movement -> unconscious fall
            motion_state = "RECUMBENT_IMMOBILITY"
            stability_score = 0.15
        elif 0.85 <= mean_mag <= 1.25 and 0.02 <= std_dev <= 0.35:
            # Rhythmic human walking cadence
            motion_state = "REGULAR_GAIT_WALKING"
            stability_score = 0.90
        elif 0.90 <= mean_mag <= 1.10 and std_dev < 0.05:
            # Standing still calmly
            motion_state = "CALM_STATIONARY"
            stability_score = 0.95
        else:
            motion_state = "MODERATE_ACTIVITY"
            stability_score = 0.65

        return {
            "stability_score": round(stability_score, 2),
            "motion_state": motion_state,
            "is_struggle": is_struggle,
            "is_fall_shock": is_fall_shock,
            "mean_accel_g": round(mean_mag, 2),
            "variance": round(variance, 3),
            "max_accel_g": round(max_mag, 2),
            "max_gyro_dps": round(max_gyro, 1)
        }

    def evaluate_biometric_recovery(
        self,
        heart_rate_bpm: float,
        baseline_bpm: float = 75.0,
        stress_score: float = 20.0
    ) -> Dict[str, Any]:
        """
        Assesses vital signs for panic recovery vs acute shock.
        """
        if heart_rate_bpm <= 0:
            return {"stability_score": 0.50, "state": "UNMONITORED"}

        diff = heart_rate_bpm - baseline_bpm

        if diff <= 15.0 and stress_score < 35.0:
            stability_score = 0.92
            state = "CALM_NORMAL"
        elif diff <= 25.0 and stress_score < 60.0:
            stability_score = 0.65
            state = "MILD_ELEVATION"
        elif diff > 40.0 or stress_score >= 80.0 or heart_rate_bpm >= 125.0:
            stability_score = 0.10
            state = "ACUTE_PANIC_TACHYCARDIA"
        else:
            stability_score = 0.40
            state = "MODERATE_ELEVATION"

        return {
            "stability_score": round(stability_score, 2),
            "state": state,
            "bpm": heart_rate_bpm,
            "stress_score": stress_score
        }

    def classify_speech_intent(self, transcript: Optional[str]) -> Dict[str, Any]:
        """
        Analyzes verbal speech captured during verification window.
        Detects cancellation intent vs subtle duress coercion phrases.
        """
        if not transcript:
            return {
                "intent": "SILENT",
                "is_duress": False,
                "confidence": 0.50
            }

        text = transcript.lower().strip()

        # Check for coercion / duress indicators first
        for duress_word in self.DURESS_KEYWORDS:
            if duress_word in text:
                return {
                    "intent": "DURESS",
                    "is_duress": True,
                    "matched_keyword": duress_word,
                    "confidence": 0.95
                }

        # Check for normal cancellation keywords
        for cancel_word in self.CANCEL_KEYWORDS:
            if cancel_word in text:
                return {
                    "intent": "CANCEL",
                    "is_duress": False,
                    "matched_keyword": cancel_word,
                    "confidence": 0.90
                }

        return {
            "intent": "UNCERTAIN",
            "is_duress": False,
            "confidence": 0.50
        }

    def verify_pin(
        self,
        entered_pin: str,
        expected_pin: str = "1234",
        configured_duress_pin: Optional[str] = None
    ) -> Tuple[str, bool]:
        """
        Validates cancellation PIN against dual-code security architecture:
        - Normal PIN -> Valid cancellation ('VALID_CANCEL', True)
        - Duress PIN -> Covert duress escalation ('DURESS_TRIGGERED', True)
        - Wrong PIN -> Rejection ('INVALID_PIN', False)
        """
        entered_pin = str(entered_pin).strip()
        expected_pin = str(expected_pin).strip()

        # Reverse PIN of expected PIN is an automatic duress code (e.g. 1234 -> 4321)
        reverse_pin = expected_pin[::-1] if len(expected_pin) > 1 and expected_pin != expected_pin[::-1] else None

        # Check Duress match
        if (configured_duress_pin and entered_pin == str(configured_duress_pin).strip()) or \
           (reverse_pin and entered_pin == reverse_pin) or \
           (entered_pin in self.UNIVERSAL_DURESS_PINS and entered_pin != expected_pin):
            return "DURESS_TRIGGERED", True

        # Check Normal Cancel match
        if entered_pin == expected_pin:
            return "VALID_CANCEL", True

        return "INVALID_PIN", False

    def assess_false_alarm(
        self,
        motion_samples: Optional[List[Any]] = None,
        heart_rate_bpm: float = 75.0,
        baseline_bpm: float = 75.0,
        stress_score: float = 20.0,
        speech_transcript: Optional[str] = None,
        entered_pin: Optional[str] = None,
        expected_pin: str = "1234",
        duress_pin: Optional[str] = None,
        elapsed_seconds: float = 0.0,
        trigger_type: str = "BUTTON"
    ) -> Dict[str, Any]:
        """
        Fuses post-trigger signals to compute false alarm probability and recommended action.
        """
        remaining_s = max(0.0, self.grace_window_seconds - elapsed_seconds)
        window_expired = elapsed_seconds >= self.grace_window_seconds

        gait_eval = self.evaluate_gait_regularity(motion_samples)
        biometric_eval = self.evaluate_biometric_recovery(heart_rate_bpm, baseline_bpm, stress_score)
        speech_eval = self.classify_speech_intent(speech_transcript)

        # Check PIN if provided
        pin_status = None
        is_pin_valid = False
        is_duress = speech_eval["is_duress"]

        if entered_pin is not None:
            pin_status, is_pin_valid = self.verify_pin(entered_pin, expected_pin, duress_pin)
            if pin_status == "DURESS_TRIGGERED":
                is_duress = True

        # Base Bayesian prior based on trigger type
        # Mechanical/touch buttons have higher false alarm prior than multi-sensor fusion
        prior_false_alarm = 0.40 if trigger_type in {"BUTTON", "TOUCH", "CLAP"} else 0.15

        # Weighted calculation of evidence
        # Weights: Gait (0.35), Biometrics (0.25), Speech (0.30), Prior (0.10)
        gait_stab = gait_eval["stability_score"]
        bio_stab = biometric_eval["stability_score"]

        speech_prob = 0.50
        if speech_eval["intent"] == "CANCEL":
            speech_prob = 0.90
        elif speech_eval["intent"] == "DURESS":
            speech_prob = 0.01

        computed_prob = (
            0.35 * gait_stab +
            0.25 * bio_stab +
            0.30 * speech_prob +
            0.10 * prior_false_alarm
        )

        # Critical Overrides:
        if is_duress:
            computed_prob = 0.0
            recommendation = "SILENT_DURESS"
        elif pin_status == "VALID_CANCEL":
            computed_prob = 0.99
            recommendation = "AUTO_SUPPRESS"
        elif gait_eval["is_struggle"] or gait_eval["is_fall_shock"] or bio_stab <= 0.15:
            computed_prob = min(computed_prob, 0.10)
            recommendation = "IMMEDIATE_ESCALATE"
        elif window_expired:
            recommendation = "AUTO_ESCALATE_EXPIRED"
        elif computed_prob >= 0.80 and speech_eval["intent"] == "CANCEL":
            recommendation = "CONFIRM_SAFE"
        elif computed_prob >= 0.70:
            recommendation = "REQUIRE_PIN"
        else:
            recommendation = "IMMEDIATE_ESCALATE"

        return {
            "false_alarm_probability": round(computed_prob, 3),
            "recommendation": recommendation,
            "is_duress": is_duress,
            "pin_status": pin_status,
            "is_pin_valid": is_pin_valid,
            "gait_analysis": gait_eval,
            "biometric_analysis": biometric_eval,
            "speech_analysis": speech_eval,
            "grace_window": {
                "total_seconds": self.grace_window_seconds,
                "elapsed_seconds": round(elapsed_seconds, 1),
                "remaining_seconds": round(remaining_s, 1),
                "window_expired": window_expired
            }
        }


# Singleton accessor
_false_alarm_filter = None

def get_false_alarm_filter() -> FalseAlarmFilter:
    global _false_alarm_filter
    if _false_alarm_filter is None:
        _false_alarm_filter = FalseAlarmFilter()
    return _false_alarm_filter
