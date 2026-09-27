import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env if present
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    """Base Configuration"""
    APP_NAME = "SafeRoute Saheli"
    VERSION = "1.0.0"
    SECRET_KEY = os.getenv("SECRET_KEY", "saheli_super_secret_flask_key_2026_default")
    JWT_SECRET = os.getenv("JWT_SECRET", "saheli_super_secret_jwt_key_2026_default")
    JWT_EXPIRATION_DELTA = timedelta(hours=int(os.getenv("JWT_EXPIRATION_HOURS", 24)))
    JWT_REFRESH_EXPIRATION_DELTA = timedelta(days=int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", 30)))
    
    # Database Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "saheli_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "saheli_password")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "saferoute_saheli")

    # If DATABASE_URL is explicitly set, use it; otherwise build MySQL URI or SQLite fallback
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, 'saferoute_saheli.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # Redis & Pub/Sub
    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

    # Firebase Admin SDK Configuration
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "saferoute-saheli-prod")
    FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "")

    # Emergency Services & Providers
    TEST_MODE = os.getenv("TEST_MODE", "true").lower() in ("true", "1", "yes")
    SMS_PROVIDER = os.getenv("SMS_PROVIDER", "MockSMSProvider")
    SMS_API_KEY = os.getenv("SMS_API_KEY", "")
    SMS_API_SECRET = os.getenv("SMS_API_SECRET", "")
    SMS_SENDER_ID = os.getenv("SMS_SENDER_ID", "SAHELI")

    VOICE_PROVIDER = os.getenv("VOICE_PROVIDER", "MockVoiceProvider")
    VOICE_API_KEY = os.getenv("VOICE_API_KEY", "")
    VOICE_API_SECRET = os.getenv("VOICE_API_SECRET", "")
    VOICE_CALLER_NUMBER = os.getenv("VOICE_CALLER_NUMBER", "+18005550199")

    # Storage Settings
    STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local")
    UPLOAD_FOLDER = os.path.join(basedir, os.getenv("UPLOAD_FOLDER", "uploads"))
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB upload limit

    # IoT Security Secrets
    CAMERA_STREAM_SECRET = os.getenv("CAMERA_STREAM_SECRET", "esp32cam_hmac_secret_token_saheli_2026")
    DEVICE_SECRET = os.getenv("DEVICE_SECRET", "wearable_esp32_hmac_shared_secret_2026")
    SESSION_TOKEN_SALT = os.getenv("SESSION_TOKEN_SALT", "tracking_salt_token_2026")

    # Emergency Timings
    EMERGENCY_GPS_INTERVAL_SEC = 5
    NORMAL_GPS_INTERVAL_SEC = 25
    TRACKING_TOKEN_EXPIRY_HOURS = 12

    # Brand Identity Colors
    BRAND_COLOR_PRIMARY = "#002350"
    BRAND_COLOR_SECONDARY = "#D2AE39"
    BRAND_COLOR_BACKGROUND = "#F5F7FA"


class DevelopmentConfig(Config):
    DEBUG = True
    TEST_MODE = True


class ProductionConfig(Config):
    DEBUG = False
    TEST_MODE = False
    # In production, default directly to MySQL URL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}"
    )


class TestingConfig(Config):
    TESTING = True
    TEST_MODE = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
