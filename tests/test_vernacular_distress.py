"""
SafeRoute Saheli — Test Suite for Phase 33:
Multi-Language Vernacular Audio Distress Engine
Validates phonetic keyword spotting across Hindi, Bengali, Tamil, Telugu, Marathi, Kannada,
fuzzy transliteration matching, and acoustic scream fusion.
"""

import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.emergency import EmergencyIncident
from backend.app.auth.jwt_handler import create_access_token
from ai_ml.models.vernacular_distress_detector import get_vernacular_detector

class TestVernacularDistressEngine(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.saheli = User(
            name="Ananya Roy",
            email="ananya.vernacular@saheli.org",
            phone="+919876543233",
            is_active=True
        )
        self.saheli.set_password("SaheliSecure@123")
        db.session.add(self.saheli)
        db.session.commit()

        self.detector = get_vernacular_detector()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_hindi_and_hinglish_distress(self):
        """Test Hindi Devanagari and Hinglish transliterations"""
        # Devanagari
        res1 = self.detector.evaluate_text_phrase("अरे बचाओ मुझे कोई मदद करो")
        self.assertTrue(res1["is_distress"])
        self.assertEqual(res1["language"], "HINDI")
        self.assertEqual(res1["urgency"], "CRITICAL")

        # Hinglish
        res2 = self.detector.evaluate_text_phrase("chhodo mujhe please!")
        self.assertTrue(res2["is_distress"])
        self.assertEqual(res2["language"], "HINDI")

    def test_bengali_distress(self):
        """Test Bengali native script and romanized phrases"""
        # Bengali native script
        res1 = self.detector.evaluate_text_phrase("বাঁচাও আমাকে সাহায্য করুন")
        self.assertTrue(res1["is_distress"])
        self.assertEqual(res1["language"], "BENGALI")

        # Romanized Bengali
        res2 = self.detector.evaluate_text_phrase("amake chhere din banchao")
        self.assertTrue(res2["is_distress"])
        self.assertEqual(res2["language"], "BENGALI")

    def test_tamil_distress(self):
        """Test Tamil native script and romanized phrases"""
        # Tamil native script
        res1 = self.detector.evaluate_text_phrase("காப்பாத்துங்க உதவி")
        self.assertTrue(res1["is_distress"])
        self.assertEqual(res1["language"], "TAMIL")

        # Romanized Tamil
        res2 = self.detector.evaluate_text_phrase("ennai vidungal kaappathunga")
        self.assertTrue(res2["is_distress"])
        self.assertEqual(res2["language"], "TAMIL")

    def test_telugu_distress(self):
        """Test Telugu native script and romanized phrases"""
        # Telugu native script
        res1 = self.detector.evaluate_text_phrase("కాపాడండి సహాయం చేయండి")
        self.assertTrue(res1["is_distress"])
        self.assertEqual(res1["language"], "TELUGU")

        # Romanized Telugu
        res2 = self.detector.evaluate_text_phrase("nannu vadileyandi kaapadandi")
        self.assertTrue(res2["is_distress"])
        self.assertEqual(res2["language"], "TELUGU")

    def test_marathi_distress(self):
        """Test Marathi native script and romanized phrases"""
        # Marathi native
        res1 = self.detector.evaluate_text_phrase("वाचवा मला धावा धावा")
        self.assertTrue(res1["is_distress"])
        self.assertEqual(res1["language"], "MARATHI")

        # Romanized Marathi
        res2 = self.detector.evaluate_text_phrase("mala soda vachva")
        self.assertTrue(res2["is_distress"])
        self.assertEqual(res2["language"], "MARATHI")

    def test_phonetic_fuzzy_transliteration(self):
        """Test robust phonetic fuzzy matching for slurred or typo speech inputs"""
        # Slurred variations: "bchao", "kapathunga", "vachwa"
        res_fuzzy1 = self.detector.evaluate_text_phrase("koi to bchao yahan")
        self.assertTrue(res_fuzzy1["is_distress"])
        self.assertGreaterEqual(res_fuzzy1["similarity"], 0.78)

        res_fuzzy2 = self.detector.evaluate_text_phrase("kapathunga ennai")
        self.assertTrue(res_fuzzy2["is_distress"])
        self.assertEqual(res_fuzzy2["language"], "TAMIL")

    def test_acoustic_scream_fusion(self):
        """Test multi-modal fusion of acoustic scream features with speech"""
        # 1. High-energy vocal scream + distress word -> Top confidence
        res_scream = self.detector.fuse_vernacular_distress(
            text_phrase="bachao",
            rms=0.22,
            spectral_centroid=3100.0,
            zcr=0.15
        )
        self.assertTrue(res_scream["is_distress"])
        self.assertEqual(res_scream["state"], "CONFIRMED_VERNACULAR_SCREAM_DISTRESS")
        self.assertGreaterEqual(res_scream["confidence"], 0.95)

        # 2. Pure acoustic scream without recognizable words
        res_pure_scream = self.detector.fuse_vernacular_distress(
            text_phrase="aaaaahhh",
            rms=0.25,
            spectral_centroid=2900.0,
            zcr=0.18
        )
        self.assertTrue(res_pure_scream["is_distress"])
        self.assertTrue(res_pure_scream["acoustic_elevation_detected"])

        # 3. Normal calm conversational audio
        res_calm = self.detector.fuse_vernacular_distress(
            text_phrase="hello how are you today",
            rms=0.03,
            spectral_centroid=750.0,
            zcr=0.02
        )
        self.assertFalse(res_calm["is_distress"])
        self.assertEqual(res_calm["state"], "NORMAL_AMBIENT_SPEECH")

    def test_rest_api_vernacular_distress_auto_trigger(self):
        """Test REST API POST /api/audio/vernacular-distress with auto_trigger=True"""
        token = create_access_token(self.saheli.id, role='SAHELI')
        headers = {'Authorization': f'Bearer {token}'}

        response = self.client.post(
            '/api/audio/vernacular-distress',
            headers=headers,
            json={
                'phrase': 'bachao bachao mujhe bachao',
                'rms': 0.18,
                'spectral_centroid': 2600.0,
                'auto_trigger': True,
                'latitude': 28.5355,
                'longitude': 77.3910,
                'battery_percent': 92
            }
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["is_distress"])
        self.assertTrue(data["emergency_triggered"])
        self.assertIsNotNone(data["incident"])
        self.assertEqual(data["incident"]["status"], "ACTIVE")

        # Verify database record
        incident_id = data["incident"]["incident_id"]
        db_incident = EmergencyIncident.query.get(incident_id)
        self.assertEqual(db_incident.trigger_type, "VERNACULAR_VOICE")
        self.assertEqual(db_incident.user_id, self.saheli.id)


if __name__ == '__main__':
    unittest.main()
