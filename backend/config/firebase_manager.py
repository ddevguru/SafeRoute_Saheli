import os
import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Manages Firebase Admin SDK initialization and messaging credentials"""
    _initialized = False

    @classmethod
    def initialize(cls, app=None):
        if cls._initialized:
            return

        cfg = app.config if app else current_app.config
        test_mode = cfg.get('TEST_MODE', True)

        if test_mode:
            logger.info("[FirebaseManager] Running in TEST_MODE: Mock FCM dispatcher active.")
            cls._initialized = True
            return

        try:
            import firebase_admin
            from firebase_admin import credentials

            cred_path = cfg.get('FIREBASE_CREDENTIALS_PATH')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                logger.info(f"[FirebaseManager] Initialized with certificate file: {cred_path}")
            elif cfg.get('FIREBASE_PRIVATE_KEY') and cfg.get('FIREBASE_CLIENT_EMAIL'):
                cred_dict = {
                    "type": "service_account",
                    "project_id": cfg.get('FIREBASE_PROJECT_ID'),
                    "private_key": cfg.get('FIREBASE_PRIVATE_KEY'),
                    "client_email": cfg.get('FIREBASE_CLIENT_EMAIL'),
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                logger.info("[FirebaseManager] Initialized with environment credentials.")
            else:
                logger.warning("[FirebaseManager] No Firebase credentials provided. Falling back to test mode.")
                cls._initialized = True
        except Exception as ex:
            logger.error(f"[FirebaseManager] Initialization failed: {ex}")
            cls._initialized = True
