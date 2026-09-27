import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FirebaseAdminClient:
    """
    Production-ready Firebase Admin Client for Cloud Messaging (FCM).
    Supports:
    1. Credentials from JSON file (FIREBASE_CREDENTIALS_PATH)
    2. Credentials from environment variables (FIREBASE_PROJECT_ID, FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY)
    3. Graceful Mock / Fallback mode for local testing without crashing
    """

    _app = None
    _is_mock = False
    _initialized = False

    @classmethod
    def initialize(cls, config=None):
        """Initialize Firebase Admin SDK with credentials or mock fallback"""
        if cls._initialized:
            return cls._app

        test_mode = getattr(config, 'TEST_MODE', True) if config else True
        cred_path = getattr(config, 'FIREBASE_CREDENTIALS_PATH', '') if config else os.getenv('FIREBASE_CREDENTIALS_PATH', '')
        project_id = getattr(config, 'FIREBASE_PROJECT_ID', '') if config else os.getenv('FIREBASE_PROJECT_ID', '')
        client_email = getattr(config, 'FIREBASE_CLIENT_EMAIL', '') if config else os.getenv('FIREBASE_CLIENT_EMAIL', '')
        private_key = getattr(config, 'FIREBASE_PRIVATE_KEY', '') if config else os.getenv('FIREBASE_PRIVATE_KEY', '')

        # Check if real credentials are provided
        has_file_cred = cred_path and os.path.isfile(cred_path)
        has_env_cred = project_id and client_email and private_key and 'BEGIN PRIVATE KEY' in private_key

        if test_mode or (not has_file_cred and not has_env_cred):
            cls._is_mock = True
            cls._initialized = True
            logger.info("[FirebaseClient] Running in TEST / MOCK Mode. Push notifications will be logged and simulated.")
            return None

        try:
            import firebase_admin
            from firebase_admin import credentials

            if has_file_cred:
                cred = credentials.Certificate(cred_path)
            else:
                cred_dict = {
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key": private_key.replace('\\n', '\n'),
                    "client_email": client_email,
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
                cred = credentials.Certificate(cred_dict)

            try:
                cls._app = firebase_admin.get_app()
            except ValueError:
                cls._app = firebase_admin.initialize_app(cred)

            cls._is_mock = False
            cls._initialized = True
            logger.info("[FirebaseClient] Firebase Admin SDK successfully initialized for production.")
            return cls._app
        except Exception as ex:
            logger.warning(f"[FirebaseClient] Could not initialize Firebase Admin SDK ({ex}). Reverting to mock mode.")
            cls._is_mock = True
            cls._initialized = True
            return None

    @classmethod
    def send_push(
        cls,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = 'high',
        channel_id: str = 'emergency_channel',
        sound: str = 'emergency_siren'
    ) -> Dict[str, Any]:
        """
        Send a targeted high-priority FCM notification to a single device token.
        Automatically converts non-string data values to strings as required by FCM specification.
        """
        if not cls._initialized:
            cls.initialize()

        data_payload = {}
        if data:
            for k, v in data.items():
                data_payload[str(k)] = str(v) if v is not None else ''

        if cls._is_mock:
            mock_id = f"mock-fcm-{int(datetime.utcnow().timestamp() * 1000)}-{token[-6:] if len(token) >= 6 else 'dev'}"
            logger.info(f"[FirebaseClient Mock] Push to {token[:12]}... | Title: {title} | Body: {body} | Data: {data_payload}")
            return {
                'success': True,
                'message_id': mock_id,
                'status': 'DELIVERED',
                'is_mock': True
            }

        try:
            from firebase_admin import messaging

            android_config = messaging.AndroidConfig(
                priority='high' if priority == 'high' else 'normal',
                notification=messaging.AndroidNotification(
                    title=title,
                    body=body,
                    channel_id=channel_id,
                    sound=sound,
                    priority='max' if priority == 'high' else 'default',
                    default_vibrate_timings=True,
                    click_action='FLUTTER_NOTIFICATION_CLICK'
                )
            )

            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        content_available=True,
                        interruption_level='time-sensitive' if priority == 'high' else 'active'
                    )
                )
            )

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data_payload,
                token=token,
                android=android_config,
                apns=apns_config
            )

            response = messaging.send(message)
            return {
                'success': True,
                'message_id': response,
                'status': 'DELIVERED',
                'is_mock': False
            }
        except Exception as ex:
            error_str = str(ex)
            logger.error(f"[FirebaseClient] Push failed to token {token[:12]}...: {error_str}")
            return {
                'success': False,
                'error': error_str,
                'status': 'FAILED',
                'is_mock': False
            }

    @classmethod
    def send_multicast(
        cls,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = 'high',
        channel_id: str = 'emergency_channel',
        sound: str = 'emergency_siren'
    ) -> Dict[str, Any]:
        """
        Send notification to multiple device tokens.
        Prunes inactive / unregistered tokens from return summary.
        """
        if not tokens:
            return {'total': 0, 'success_count': 0, 'failure_count': 0, 'results': []}

        success_count = 0
        failure_count = 0
        results = []
        dead_tokens = []

        for token in tokens:
            res = cls.send_push(
                token=token,
                title=title,
                body=body,
                data=data,
                priority=priority,
                channel_id=channel_id,
                sound=sound
            )
            if res.get('success'):
                success_count += 1
            else:
                failure_count += 1
                err = res.get('error', '').lower()
                if 'not-registered' in err or 'invalid-registration-token' in err:
                    dead_tokens.append(token)

            results.append({
                'token': token,
                'status': res.get('status'),
                'message_id': res.get('message_id'),
                'error': res.get('error')
            })

        return {
            'total': len(tokens),
            'success_count': success_count,
            'failure_count': failure_count,
            'dead_tokens': dead_tokens,
            'results': results
        }
