"""
SafeRoute Saheli — Multi-Language Vernacular Audio Distress Engine
Detects spoken distress, screams, and assault cries across 6 major Indian languages:
Hindi/Hinglish, Bengali, Tamil, Telugu, Marathi, Kannada, plus English.
Supports both native Indic scripts (Devanagari, Bengali, Tamil, Telugu, Kannada)
and Romanized phonetic transliterations with fuzzy acoustic-phonetic distance matching.
"""

import re
import math
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class VernacularDistressDetector:
    """
    Multi-Lingual Audio & Text Distress Spotting Engine for Women Safety.
    """

    DISTRESS_DICTIONARY = {
        "HINDI": {
            "native": [
                "बचाओ", "बचाओ बचाओ", "मदद करो", "मदद", "छोड़ो मुझे", "छोड़ो",
                "पुलिस", "रुको", "मुसीबत", "जाने दो", "मार डालेगा", "सहायता"
            ],
            "romanized": [
                "bachao", "bachao bachao", "madad karo", "madad", "chhodo mujhe",
                "chhodo", "choro mujhe", "police", "ruko", "musibat", "jane do",
                "maar dalega", "sahayata", "bchao", "bachhao"
            ],
            "urgency": "CRITICAL"
        },
        "BENGALI": {
            "native": [
                "বাঁচাও", "বাঁচাও আমাকে", "সাহায্য করুন", "সাহায্য", "আমাকে ছেড়ে দিন",
                "পুলিশ ডাকুন", "রক্ষা করুন"
            ],
            "romanized": [
                "banchao", "banchao amake", "sahajjo korun", "sahajjo", "amake chhere din",
                "police dakun", "roksha korun", "banchao banchao"
            ],
            "urgency": "CRITICAL"
        },
        "TAMIL": {
            "native": [
                "காப்பாத்துங்க", "உதவி", "என்னை விடுங்கள்", "போலீஸ்", "காப்பாத்து",
                "உதவுங்கள்"
            ],
            "romanized": [
                "kaappathunga", "kapathunga", "kaapaathunga", "udhavi", "ennai vidungal",
                "police", "kaappathu", "udhavungal"
            ],
            "urgency": "CRITICAL"
        },
        "TELUGU": {
            "native": [
                "కాపాడండి", "సహాయం", "సహాయం చేయండి", "నన్ను వదిలేయండి", "పోలీస్",
                "కాపాడండి కాపాడండి"
            ],
            "romanized": [
                "kaapadandi", "kapadandi", "sahaayam", "sahayam", "sahaayam cheyandi",
                "nannu vadileyandi", "police"
            ],
            "urgency": "CRITICAL"
        },
        "MARATHI": {
            "native": [
                "वाचवा", "वाचवा मला", "मदत करा", "मदत", "मला सोडा", "धावा धावा",
                "पोलीस", "धावा"
            ],
            "romanized": [
                "vachva", "vachva mala", "madat kara", "madat", "mala soda",
                "dhava dhava", "dhava", "police", "vachwa"
            ],
            "urgency": "CRITICAL"
        },
        "KANNADA": {
            "native": [
                "ಕಾಪಾಡಿ", "ಸಹಾಯ ಮಾಡಿ", "ನನ್ನನ್ನು ಬಿಡಿ", "ಪೊಲೀಸ್", "ಸಹಾಯ"
            ],
            "romanized": [
                "kaapadi", "kapadi", "sahaaya maadi", "sahaya", "nannannu bidi",
                "police"
            ],
            "urgency": "CRITICAL"
        },
        "ENGLISH": {
            "native": [
                "help", "help me", "save me", "please save me", "emergency",
                "call the police", "stop it", "get off me", "dont touch me"
            ],
            "romanized": [
                "help", "help me", "save me", "please save me", "emergency",
                "call the police", "stop it", "get off me", "dont touch me"
            ],
            "urgency": "HIGH"
        }
    }

    def __init__(self, phonetic_threshold: float = 0.78):
        self.phonetic_threshold = phonetic_threshold

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Compute Levenshtein edit distance between two strings"""
        if len(s1) < len(s2):
            return VernacularDistressDetector._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def _similarity_ratio(s1: str, s2: str) -> float:
        """Normalized similarity ratio (0.0 to 1.0)"""
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        dist = VernacularDistressDetector._levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        return 1.0 - (dist / max_len)

    def evaluate_text_phrase(self, raw_input: str) -> Dict[str, Any]:
        """
        Evaluates input text against multi-lingual distress lexicon.
        Checks both exact matching and fuzzy phonetic distance.
        """
        if not raw_input or not str(raw_input).strip():
            return {
                "is_distress": False,
                "confidence": 0.0,
                "language": None,
                "matched_keyword": None,
                "urgency": "NONE",
                "similarity": 0.0
            }

        import string
        punctuation_set = set(string.punctuation + "।॥‘’“”–—…!?¡¿,.;:'\"-()[]{}")
        cleaned = str(raw_input).lower().strip()
        # Remove only punctuation, preserving all Unicode Indic vowels and combining characters
        normalized = "".join(ch for ch in cleaned if ch not in punctuation_set)
        tokens = normalized.split()

        best_match = {
            "is_distress": False,
            "confidence": 0.0,
            "language": None,
            "matched_keyword": None,
            "urgency": "NONE",
            "similarity": 0.0
        }

        # 1. First Pass: Substring & Exact Match across all languages
        for lang, lexicon in self.DISTRESS_DICTIONARY.items():
            all_words = lexicon["native"] + lexicon["romanized"]
            for target in all_words:
                target_clean = target.lower().strip()
                # Exact or full substring match
                if target_clean in normalized or target_clean == normalized:
                    conf = 0.98 if target_clean in {"bachao", "banchao", "kaappathunga", "kaapadandi", "vachva", "बचाओ", "বাঁচাও", "காப்பாத்துங்க", "ಕಾಪಾಡಿ"} else 0.92
                    return {
                        "is_distress": True,
                        "confidence": conf,
                        "language": lang,
                        "matched_keyword": target,
                        "urgency": lexicon["urgency"],
                        "similarity": 1.0
                    }

        # 2. Second Pass: Token-level Fuzzy Match
        for token in tokens:
            if len(token) < 3:
                continue
            for lang, lexicon in self.DISTRESS_DICTIONARY.items():
                for target in lexicon["romanized"] + lexicon["native"]:
                    target_clean = target.lower().strip()
                    # Skip multi-word targets in single token check
                    if " " in target_clean:
                        target_words = target_clean.split()
                        target_word = target_words[0]
                    else:
                        target_word = target_clean

                    sim = self._similarity_ratio(token, target_word)
                    if sim >= self.phonetic_threshold and sim > best_match["similarity"]:
                        conf = round(min(0.95, sim * 0.95), 2)
                        best_match = {
                            "is_distress": True,
                            "confidence": conf,
                            "language": lang,
                            "matched_keyword": target,
                            "urgency": lexicon["urgency"],
                            "similarity": round(sim, 3)
                        }

        return best_match

    def evaluate_acoustic_features(
        self,
        rms: float = 0.0,
        spectral_centroid: float = 0.0,
        zcr: float = 0.0,
        peak: float = 0.0
    ) -> Dict[str, Any]:
        """
        Assesses raw acoustic signal DSP features for distress screams:
        High acoustic energy (RMS > 0.12) + high centroid (> 2200 Hz) indicates screams.
        """
        is_acoustic_distress = False
        acoustic_score = 0.0

        if rms > 0.12 and spectral_centroid > 2000.0:
            is_acoustic_distress = True
            centroid_factor = min(1.0, (spectral_centroid - 2000.0) / 2500.0)
            rms_factor = min(1.0, (rms - 0.10) / 0.50)
            acoustic_score = 0.70 + 0.15 * centroid_factor + 0.15 * rms_factor
        elif rms > 0.20 or peak > 0.85:
            is_acoustic_distress = True
            acoustic_score = 0.65
        else:
            acoustic_score = 0.10

        return {
            "is_acoustic_distress": is_acoustic_distress,
            "acoustic_score": round(min(0.98, acoustic_score), 2),
            "rms": rms,
            "spectral_centroid": spectral_centroid,
            "zcr": zcr
        }

    def fuse_vernacular_distress(
        self,
        text_phrase: Optional[str] = None,
        rms: float = 0.0,
        spectral_centroid: float = 0.0,
        zcr: float = 0.0,
        peak: float = 0.0
    ) -> Dict[str, Any]:
        """
        Holistically fuses vernacular linguistic keywords with acoustic signal features.
        """
        text_eval = self.evaluate_text_phrase(text_phrase)
        acoustic_eval = self.evaluate_acoustic_features(rms=rms, spectral_centroid=spectral_centroid, zcr=zcr, peak=peak)

        text_conf = text_eval["confidence"]
        acoustic_conf = acoustic_eval["acoustic_score"]

        # Fusion rules
        if text_eval["is_distress"] and acoustic_eval["is_acoustic_distress"]:
            fused_conf = min(0.99, text_conf * 0.70 + acoustic_conf * 0.35)
            is_distress = True
            state = "CONFIRMED_VERNACULAR_SCREAM_DISTRESS"
        elif text_eval["is_distress"]:
            fused_conf = text_conf
            is_distress = True
            state = "VERNACULAR_KEYWORD_DISTRESS"
        elif acoustic_eval["is_acoustic_distress"] and acoustic_conf >= 0.75:
            fused_conf = acoustic_conf
            is_distress = True
            state = "ACOUSTIC_SCREAM_DISTRESS"
        else:
            fused_conf = max(text_conf, acoustic_conf)
            is_distress = False
            state = "NORMAL_AMBIENT_SPEECH"

        return {
            "is_distress": is_distress,
            "confidence": round(fused_conf, 3),
            "state": state,
            "detected_language": text_eval["language"],
            "matched_keyword": text_eval["matched_keyword"],
            "urgency": text_eval["urgency"],
            "phonetic_similarity": text_eval["similarity"],
            "acoustic_elevation_detected": acoustic_eval["is_acoustic_distress"],
            "text_analysis": text_eval,
            "acoustic_analysis": acoustic_eval
        }


# Singleton instance
_vernacular_detector = None

def get_vernacular_detector() -> VernacularDistressDetector:
    global _vernacular_detector
    if _vernacular_detector is None:
        _vernacular_detector = VernacularDistressDetector()
    return _vernacular_detector
