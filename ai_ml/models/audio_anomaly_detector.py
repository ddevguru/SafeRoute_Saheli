"""
SafeRoute Saheli — Acoustic Distress & Keyword Classifier
Extracts DSP features (RMS, ZCR, Spectral Centroid, Rolloff) to detect screams, cries, and distress spikes.
"""

import math
from typing import Dict, Any, List
import numpy as np

class AudioAnomalyDetector:
    """
    Acoustic feature extractor and pattern classifier for women safety distress detection
    """
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def extract_features(self, signal: np.ndarray) -> Dict[str, float]:
        """Extract key acoustic parameters from 1D audio sample array"""
        if len(signal) == 0:
            return {"rms": 0.0, "zcr": 0.0, "spectral_centroid": 0.0, "peak": 0.0}

        # 1. Peak & RMS Energy
        peak = float(np.max(np.abs(signal)))
        rms = float(np.sqrt(np.mean(signal ** 2)))

        # 2. Zero Crossing Rate (ZCR)
        signs = np.sign(signal)
        signs[signs == 0] = 1
        zcr = float(np.mean(np.abs(np.diff(signs))) / 2.0)

        # 3. FFT & Spectral Centroid
        # High spectral centroid is characteristic of high-pitched female screams & sirens
        fft_vals = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal), d=1.0 / self.sample_rate)

        sum_fft = np.sum(fft_vals)
        if sum_fft > 1e-6:
            centroid = float(np.sum(freqs * fft_vals) / sum_fft)
        else:
            centroid = 0.0

        return {
            "peak": round(peak, 4),
            "rms": round(rms, 4),
            "zcr": round(zcr, 4),
            "spectral_centroid": round(centroid, 1)
        }

    def classify_audio(self, signal_or_features: Any) -> Dict[str, Any]:
        """
        Classifies audio stream into safety states:
        - SCREAM_OR_SHOUT
        - GLASS_BREAK_OR_CRASH
        - CRYING_OR_DISTRESS
        - CLAP_OR_TAP
        - NORMAL_SPEECH
        - AMBIENT_NOISE
        """
        if isinstance(signal_or_features, np.ndarray):
            features = self.extract_features(signal_or_features)
        elif isinstance(signal_or_features, dict):
            features = signal_or_features
        else:
            features = {"peak": 0.0, "rms": 0.0, "zcr": 0.0, "spectral_centroid": 0.0}

        rms = features.get("rms", 0.0)
        zcr = features.get("zcr", 0.0)
        centroid = features.get("spectral_centroid", 0.0)
        peak = features.get("peak", 0.0)

        # Expert Decision Boundaries
        if peak > 0.70 and centroid > 2200.0 and rms > 0.25:
            classification = "SCREAM_OR_SHOUT"
            confidence = min(0.98, 0.75 + (centroid / 4000.0) * 0.2)
            is_emergency = True
        elif peak > 0.85 and zcr > 0.35 and centroid > 2800.0:
            classification = "GLASS_BREAK_OR_CRASH"
            confidence = 0.92
            is_emergency = True
        elif rms > 0.15 and 600.0 < centroid < 1800.0 and zcr < 0.12:
            classification = "CRYING_OR_DISTRESS"
            confidence = 0.86
            is_emergency = True
        elif peak > 0.75 and rms < 0.12 and zcr > 0.20:
            classification = "CLAP_OR_TAP"
            confidence = 0.90
            is_emergency = False
        elif rms > 0.05 and 300.0 < centroid < 2500.0:
            classification = "NORMAL_SPEECH"
            confidence = 0.88
            is_emergency = False
        else:
            classification = "AMBIENT_NOISE"
            confidence = 0.95
            is_emergency = False

        return {
            "classification": classification,
            "confidence": round(confidence, 2),
            "is_emergency": is_emergency,
            "features": features
        }


# Singleton instance
_audio_detector = None

def get_audio_detector() -> AudioAnomalyDetector:
    global _audio_detector
    if _audio_detector is None:
        _audio_detector = AudioAnomalyDetector()
    return _audio_detector
