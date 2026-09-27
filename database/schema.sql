-- SafeRoute Saheli Production MySQL Database Schema
-- Version: 1.0.0
-- Charset: utf8mb4, Collation: utf8mb4_unicode_ci

CREATE DATABASE IF NOT EXISTS saferoute_saheli CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE saferoute_saheli;

-- ============================================================================
-- 1. USERS (Saheli Accounts)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(191) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    date_of_birth DATE NULL,
    profile_photo_url VARCHAR(500) NULL,
    emergency_blood_group VARCHAR(10) NULL,
    medical_notes TEXT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    privacy_guardian_camera BOOLEAN DEFAULT TRUE,
    privacy_emergency_camera_override BOOLEAN DEFAULT TRUE,
    privacy_audio_recording BOOLEAN DEFAULT TRUE,
    privacy_live_location BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_phone (phone)
) ENGINE=InnoDB;

-- ============================================================================
-- 2. GUARDIANS
-- ============================================================================
CREATE TABLE IF NOT EXISTS guardians (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(191) NOT NULL UNIQUE,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_guardians_email (email),
    INDEX idx_guardians_username (username)
) ENGINE=InnoDB;

-- ============================================================================
-- 3. GUARDIAN_USERS (Many-to-Many Relationship)
-- ============================================================================
CREATE TABLE IF NOT EXISTS guardian_users (
    id VARCHAR(36) PRIMARY KEY,
    saheli_id VARCHAR(36) NOT NULL,
    guardian_id VARCHAR(36) NOT NULL,
    relationship_label VARCHAR(60) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    can_view_camera BOOLEAN DEFAULT FALSE,
    can_view_location BOOLEAN DEFAULT TRUE,
    emergency_override_camera BOOLEAN DEFAULT TRUE,
    invitation_status ENUM('PENDING', 'ACCEPTED', 'REVOKED') DEFAULT 'ACCEPTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (saheli_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (guardian_id) REFERENCES guardians(id) ON DELETE CASCADE,
    UNIQUE KEY uk_saheli_guardian (saheli_id, guardian_id),
    INDEX idx_gu_saheli (saheli_id),
    INDEX idx_gu_guardian (guardian_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 4. DEVICES (Wearable ESP32 & ESP32-CAM)
-- ============================================================================
CREATE TABLE IF NOT EXISTS devices (
    id VARCHAR(36) PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL UNIQUE,
    device_type ENUM('ESP32_WEARABLE', 'ESP32_CAM') NOT NULL,
    device_secret_hash VARCHAR(255) NOT NULL,
    assigned_user_id VARCHAR(36) NULL,
    nickname VARCHAR(80) NULL,
    is_paired BOOLEAN DEFAULT FALSE,
    status ENUM('ONLINE', 'OFFLINE', 'EMERGENCY', 'MAINTENANCE') DEFAULT 'OFFLINE',
    last_heartbeat TIMESTAMP NULL,
    firmware_version VARCHAR(32) DEFAULT '1.0.0',
    battery_percent INT DEFAULT 100,
    battery_voltage FLOAT DEFAULT 4.20,
    wifi_rssi INT DEFAULT -60,
    camera_health VARCHAR(50) DEFAULT 'IDLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_devices_device_id (device_id),
    INDEX idx_devices_user (assigned_user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 5. DEVICE_EVENTS (Telemetry Log)
-- ============================================================================
CREATE TABLE IF NOT EXISTS device_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    event_payload JSON NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_device_events_dev (device_id),
    INDEX idx_device_events_type (event_type),
    INDEX idx_device_events_time (timestamp)
) ENGINE=InnoDB;

-- ============================================================================
-- 6. DEVICE_TOKENS (FCM Push Notification Tokens)
-- ============================================================================
CREATE TABLE IF NOT EXISTS device_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NULL,
    guardian_id VARCHAR(36) NULL,
    fcm_token VARCHAR(500) NOT NULL UNIQUE,
    platform ENUM('ANDROID', 'IOS', 'WEB') DEFAULT 'ANDROID',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (guardian_id) REFERENCES guardians(id) ON DELETE CASCADE,
    INDEX idx_tokens_user (user_id),
    INDEX idx_tokens_guardian (guardian_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 7. EMERGENCY_CONTACTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    priority_order INT DEFAULT 1,
    notify_sms BOOLEAN DEFAULT TRUE,
    notify_call BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_ec_user (user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 8. EMERGENCY_INCIDENTS (Master Incident Table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS emergency_incidents (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    device_id VARCHAR(64) NULL,
    trigger_type ENUM('TOUCH', 'BUTTON', 'VOICE', 'CLAP', 'MOTION', 'MULTI_SIGNAL') NOT NULL,
    status ENUM('ACTIVE', 'CANCELLED', 'RESOLVED') DEFAULT 'ACTIVE',
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    accuracy_meters FLOAT DEFAULT 5.0,
    battery_percent INT DEFAULT 100,
    confidence FLOAT DEFAULT 1.0,
    cancellation_reason VARCHAR(255) NULL,
    resolved_notes TEXT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_incidents_user (user_id),
    INDEX idx_incidents_status (status),
    INDEX idx_incidents_started (started_at)
) ENGINE=InnoDB;

-- ============================================================================
-- 9. EMERGENCY_NOTIFICATIONS & NOTIFICATION_LOGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS emergency_notifications (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NOT NULL,
    recipient_type ENUM('GUARDIAN', 'EMERGENCY_CONTACT', 'POLICE') NOT NULL,
    recipient_id VARCHAR(36) NULL,
    recipient_phone VARCHAR(20) NULL,
    channel ENUM('FCM', 'SMS', 'CALL', 'SOCKET') NOT NULL,
    status ENUM('PENDING', 'SENT', 'DELIVERED', 'FAILED') DEFAULT 'PENDING',
    provider_reference VARCHAR(128) NULL,
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES emergency_incidents(id) ON DELETE CASCADE,
    INDEX idx_en_incident (incident_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notification_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    incident_id VARCHAR(36) NULL,
    channel VARCHAR(32) NOT NULL,
    destination VARCHAR(191) NOT NULL,
    payload TEXT NULL,
    status VARCHAR(32) NOT NULL,
    response_body TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nl_incident (incident_id),
    INDEX idx_nl_created (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- 10. LOCATION_HISTORY
-- ============================================================================
CREATE TABLE IF NOT EXISTS location_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    device_id VARCHAR(64) NULL,
    incident_id VARCHAR(36) NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    accuracy FLOAT DEFAULT 5.0,
    speed FLOAT DEFAULT 0.0,
    heading FLOAT DEFAULT 0.0,
    is_emergency BOOLEAN DEFAULT FALSE,
    battery_level INT DEFAULT 100,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (incident_id) REFERENCES emergency_incidents(id) ON DELETE SET NULL,
    INDEX idx_loc_user (user_id),
    INDEX idx_loc_incident (incident_id),
    INDEX idx_loc_time (recorded_at)
) ENGINE=InnoDB;

-- ============================================================================
-- 11. LIVE_TRACKING_SESSIONS & TRACKING_TOKENS
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_tracking_sessions (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    tracking_token VARCHAR(128) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES emergency_incidents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_lts_token (tracking_token),
    INDEX idx_lts_incident (incident_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tracking_tokens (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    token_value VARCHAR(128) NOT NULL UNIQUE,
    access_count INT DEFAULT 0,
    last_accessed_at TIMESTAMP NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES live_tracking_sessions(id) ON DELETE CASCADE,
    INDEX idx_tt_token (token_value)
) ENGINE=InnoDB;

-- ============================================================================
-- 12. CAMERA & AUDIO EVIDENCE TABLES
-- ============================================================================
CREATE TABLE IF NOT EXISTS camera_snapshots (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NULL,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(36) NULL,
    image_url VARCHAR(500) NOT NULL,
    storage_type ENUM('LOCAL', 'S3', 'FIREBASE') DEFAULT 'LOCAL',
    file_size_bytes BIGINT DEFAULT 0,
    file_hash VARCHAR(64) NOT NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES emergency_incidents(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_cs_incident (incident_id),
    INDEX idx_cs_device (device_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS camera_recordings (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NULL,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(36) NULL,
    storage_url VARCHAR(500) NOT NULL,
    storage_type ENUM('LOCAL', 'S3', 'FIREBASE') DEFAULT 'LOCAL',
    duration_seconds INT DEFAULT 0,
    file_size_bytes BIGINT DEFAULT 0,
    file_hash VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES emergency_incidents(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_cr_incident (incident_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audio_recordings (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NULL,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(36) NULL,
    storage_url VARCHAR(500) NOT NULL,
    storage_type ENUM('LOCAL', 'S3', 'FIREBASE') DEFAULT 'LOCAL',
    duration_seconds INT DEFAULT 0,
    file_size_bytes BIGINT DEFAULT 0,
    file_hash VARCHAR(64) NOT NULL,
    trigger_type VARCHAR(32) DEFAULT 'EMERGENCY',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES emergency_incidents(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_ar_incident (incident_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 13. SENSOR EVENT LOGS (Voice, Clap, Movement)
-- ============================================================================
CREATE TABLE IF NOT EXISTS voice_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(36) NULL,
    keyword_detected VARCHAR(64) NOT NULL,
    confidence FLOAT NOT NULL,
    audio_snippet_url VARCHAR(500) NULL,
    triggered_incident_id VARCHAR(36) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ve_dev (device_id),
    INDEX idx_ve_time (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clap_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(36) NULL,
    clap_count INT NOT NULL,
    interval_pattern_ms VARCHAR(128) NULL,
    confidence FLOAT NOT NULL,
    triggered_incident_id VARCHAR(36) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ce_dev (device_id),
    INDEX idx_ce_time (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS movement_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(36) NULL,
    accel_x FLOAT NOT NULL,
    accel_y FLOAT NOT NULL,
    accel_z FLOAT NOT NULL,
    gyro_x FLOAT NOT NULL,
    gyro_y FLOAT NOT NULL,
    gyro_z FLOAT NOT NULL,
    anomaly_type ENUM('FALL', 'STRUGGLE', 'IMPACT', 'SUDDEN_JERK') NOT NULL,
    confidence FLOAT NOT NULL,
    triggered_incident_id VARCHAR(36) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_me_dev (device_id),
    INDEX idx_me_type (anomaly_type)
) ENGINE=InnoDB;

-- ============================================================================
-- 14. ROUTING & AI SAFETY FEATURES
-- ============================================================================
CREATE TABLE IF NOT EXISTS routes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    start_lat DECIMAL(10, 7) NOT NULL,
    start_lng DECIMAL(10, 7) NOT NULL,
    dest_lat DECIMAL(10, 7) NOT NULL,
    dest_lng DECIMAL(10, 7) NOT NULL,
    route_type ENUM('SHORTEST', 'FASTEST', 'SAFETY_OPTIMIZED') NOT NULL,
    polyline_geojson JSON NOT NULL,
    total_distance_km FLOAT NOT NULL,
    estimated_duration_mins FLOAT NOT NULL,
    overall_safety_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_routes_user (user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS route_segments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    route_id VARCHAR(36) NOT NULL,
    segment_index INT NOT NULL,
    start_lat DECIMAL(10, 7) NOT NULL,
    start_lng DECIMAL(10, 7) NOT NULL,
    end_lat DECIMAL(10, 7) NOT NULL,
    end_lng DECIMAL(10, 7) NOT NULL,
    segment_safety_score FLOAT NOT NULL,
    lighting_score FLOAT DEFAULT 0.5,
    crime_score FLOAT DEFAULT 0.2,
    crowd_score FLOAT DEFAULT 0.6,
    isolation_score FLOAT DEFAULT 0.3,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE,
    INDEX idx_rs_route (route_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS route_risk_scores (
    id VARCHAR(36) PRIMARY KEY,
    route_id VARCHAR(36) NOT NULL,
    neuro_fuzzy_risk FLOAT NOT NULL,
    genetic_fitness_score FLOAT NOT NULL,
    crime_density_factor FLOAT NOT NULL,
    isolation_factor FLOAT NOT NULL,
    lighting_factor FLOAT NOT NULL,
    crowd_factor FLOAT NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS route_deviations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    route_id VARCHAR(36) NOT NULL,
    incident_id VARCHAR(36) NULL,
    expected_lat DECIMAL(10, 7) NOT NULL,
    expected_lng DECIMAL(10, 7) NOT NULL,
    actual_lat DECIMAL(10, 7) NOT NULL,
    actual_lng DECIMAL(10, 7) NOT NULL,
    deviation_distance_meters FLOAT NOT NULL,
    action_taken VARCHAR(128) DEFAULT 'RECALCULATED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS risk_features (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    radius_meters FLOAT DEFAULT 200.0,
    crime_rate FLOAT DEFAULT 0.0,
    lighting_quality FLOAT DEFAULT 1.0,
    isolation_index FLOAT DEFAULT 0.0,
    crowd_density FLOAT DEFAULT 0.5,
    police_proximity_meters FLOAT DEFAULT 1000.0,
    hospital_proximity_meters FLOAT DEFAULT 1500.0,
    historical_incident_count INT DEFAULT 0,
    data_source_label VARCHAR(64) DEFAULT 'SYNTHETIC_BENCHMARK',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_rf_coords (latitude, longitude)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS risk_predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    model_type ENUM('NEURO_FUZZY', 'GA_OPTIMIZED', 'ENSEMBLE') NOT NULL,
    risk_score FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    features_json JSON NULL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- 15. SAFE PLACES & NEARBY HELP
-- ============================================================================
CREATE TABLE IF NOT EXISTS safe_places (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category ENUM('POLICE', 'HOSPITAL', 'PHARMACY', 'SHELTER', 'TRANSPORT_HUB', 'SECURITY_BOOTH') NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone_number VARCHAR(30) NULL,
    is_24x7 BOOLEAN DEFAULT TRUE,
    verified_status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sp_category (category),
    INDEX idx_sp_coords (latitude, longitude)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nearby_help_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    incident_id VARCHAR(36) NOT NULL,
    safe_place_id VARCHAR(36) NOT NULL,
    distance_meters FLOAT NOT NULL,
    guidance_presented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES emergency_incidents(id) ON DELETE CASCADE,
    FOREIGN KEY (safe_place_id) REFERENCES safe_places(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- 16. ADMIN USERS & AUDIT LOGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS admin_users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('SUPERADMIN', 'SAFETY_OPERATOR', 'AUDITOR') DEFAULT 'SAFETY_OPERATOR',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_admin_user (username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    actor_type ENUM('USER', 'GUARDIAN', 'ADMIN', 'DEVICE', 'SYSTEM') NOT NULL,
    actor_id VARCHAR(64) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    resource_id VARCHAR(64) NULL,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(255) NULL,
    details JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_actor (actor_type, actor_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_time (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NULL,
    guardian_id VARCHAR(36) NULL,
    admin_id VARCHAR(36) NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_rt_hash (token_hash)
) ENGINE=InnoDB;
