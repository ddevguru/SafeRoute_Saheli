-- ============================================================================
-- SafeRoute Saheli Production PostgreSQL Database Schema
-- Version: 1.0.0
-- Dialect: PostgreSQL 14+ / 15+ / 16+ (Render, Supabase, AWS RDS, Neon)
-- ============================================================================

-- Enable UUID extension if available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. USERS (Saheli Primary Accounts)
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
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    privacy_guardian_camera BOOLEAN DEFAULT TRUE NOT NULL,
    privacy_emergency_camera_override BOOLEAN DEFAULT TRUE NOT NULL,
    privacy_audio_recording BOOLEAN DEFAULT TRUE NOT NULL,
    privacy_live_location BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- ============================================================================
-- 2. GUARDIANS (Trusted Contacts / Guardians)
-- ============================================================================
CREATE TABLE IF NOT EXISTS guardians (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(191) NOT NULL UNIQUE,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_guardians_email ON guardians(email);
CREATE INDEX IF NOT EXISTS idx_guardians_username ON guardians(username);

-- ============================================================================
-- 3. GUARDIAN_USERS (Many-to-Many Relationship & Permission Toggles)
-- ============================================================================
CREATE TABLE IF NOT EXISTS guardian_users (
    id VARCHAR(36) PRIMARY KEY,
    saheli_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    guardian_id VARCHAR(36) NOT NULL REFERENCES guardians(id) ON DELETE CASCADE,
    relationship_label VARCHAR(60) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    can_view_camera BOOLEAN DEFAULT FALSE NOT NULL,
    can_view_location BOOLEAN DEFAULT TRUE NOT NULL,
    can_listen_audio BOOLEAN DEFAULT FALSE NOT NULL,
    receive_sms_alerts BOOLEAN DEFAULT TRUE NOT NULL,
    receive_call_alerts BOOLEAN DEFAULT TRUE NOT NULL,
    receive_push_alerts BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_saheli_guardian UNIQUE (saheli_id, guardian_id)
);

CREATE INDEX IF NOT EXISTS idx_gu_saheli ON guardian_users(saheli_id);
CREATE INDEX IF NOT EXISTS idx_gu_guardian ON guardian_users(guardian_id);

-- ============================================================================
-- 4. EMERGENCY_CONTACTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    priority_order INTEGER DEFAULT 1 NOT NULL,
    notify_sms BOOLEAN DEFAULT TRUE NOT NULL,
    notify_call BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ec_user ON emergency_contacts(user_id);

-- ============================================================================
-- 5. DEVICES (Wearable IoT Hardware & ESP32-CAMs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS devices (
    id VARCHAR(36) PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL UNIQUE,
    assigned_user_id VARCHAR(36) NULL REFERENCES users(id) ON DELETE SET NULL,
    device_type VARCHAR(32) NOT NULL, -- WEARABLE, ESP32_CAM, SMART_PENDANT
    device_secret_hash VARCHAR(255) NOT NULL,
    firmware_version VARCHAR(32) DEFAULT '1.0.0' NOT NULL,
    battery_level INTEGER DEFAULT 100 NOT NULL,
    status VARCHAR(20) DEFAULT 'OFFLINE' NOT NULL,
    last_ping TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_devices_devid ON devices(device_id);
CREATE INDEX IF NOT EXISTS idx_devices_user ON devices(assigned_user_id);

-- ============================================================================
-- 6. EMERGENCY_INCIDENTS (Master Incident State Machine)
-- ============================================================================
CREATE TABLE IF NOT EXISTS emergency_incidents (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(64) NULL,
    trigger_type VARCHAR(32) NOT NULL, -- TOUCH, BUTTON, VOICE, CLAP, MOTION, MULTI_SIGNAL
    status VARCHAR(30) DEFAULT 'ACTIVE' NOT NULL, -- ACTIVE, DURESS_ESCALATED, CANCELLED_FALSE_ALARM, RESOLVED
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    accuracy_meters DOUBLE PRECISION DEFAULT 5.0,
    battery_percent INTEGER DEFAULT 100,
    confidence DOUBLE PRECISION DEFAULT 1.0,
    cancellation_reason VARCHAR(255) NULL,
    resolved_notes TEXT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_incidents_user ON emergency_incidents(user_id);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON emergency_incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_started ON emergency_incidents(started_at);

-- ============================================================================
-- 7. LIVE_TRACKING_SESSIONS & TRACKING_TOKENS
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_tracking_sessions (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NOT NULL REFERENCES emergency_incidents(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tracking_token VARCHAR(64) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_lts_token ON live_tracking_sessions(tracking_token);

CREATE TABLE IF NOT EXISTS tracking_tokens (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES live_tracking_sessions(id) ON DELETE CASCADE,
    token_value VARCHAR(64) NOT NULL UNIQUE,
    last_accessed_at TIMESTAMP WITH TIME ZONE NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================================================================
-- 8. LOCATION_HISTORY
-- ============================================================================
CREATE TABLE IF NOT EXISTS location_history (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NULL REFERENCES emergency_incidents(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    accuracy_meters DOUBLE PRECISION DEFAULT 5.0,
    battery_percent INTEGER DEFAULT 100,
    speed_mps DOUBLE PRECISION DEFAULT 0.0,
    heading_deg DOUBLE PRECISION DEFAULT 0.0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_lh_incident ON location_history(incident_id);
CREATE INDEX IF NOT EXISTS idx_lh_recorded ON location_history(recorded_at);

-- ============================================================================
-- 9. CAMERA_SNAPSHOTS & CAMERA_RECORDINGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS camera_snapshots (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NULL REFERENCES emergency_incidents(id) ON DELETE SET NULL,
    device_id VARCHAR(36) NULL REFERENCES devices(id) ON DELETE SET NULL,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    file_size_bytes INTEGER DEFAULT 0,
    file_hash VARCHAR(64) NOT NULL,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS camera_recordings (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NULL REFERENCES emergency_incidents(id) ON DELETE SET NULL,
    device_id VARCHAR(36) NULL REFERENCES devices(id) ON DELETE SET NULL,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recording_url VARCHAR(500) NOT NULL,
    duration_seconds INTEGER DEFAULT 0,
    file_size_bytes INTEGER DEFAULT 0,
    file_hash VARCHAR(64) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE NULL
);

-- ============================================================================
-- 10. AUDIO_RECORDINGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS audio_recordings (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NULL REFERENCES emergency_incidents(id) ON DELETE SET NULL,
    device_id VARCHAR(36) NULL REFERENCES devices(id) ON DELETE SET NULL,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    storage_url VARCHAR(500) NOT NULL,
    duration_seconds INTEGER DEFAULT 0,
    file_size_bytes INTEGER DEFAULT 0,
    file_hash VARCHAR(64) NOT NULL,
    trigger_type VARCHAR(50) DEFAULT 'EMERGENCY',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================================================================
-- 11. SAFE_PLACES & SAFE_ZONES (Geo-Fence Perimeters)
-- ============================================================================
CREATE TABLE IF NOT EXISTS safe_places (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL, -- POLICE_STATION, HOSPITAL, PHARMACY, WOMEN_SHELTER, METRO_STATION
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(30) NULL,
    is_24x7 BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sp_category ON safe_places(category);

CREATE TABLE IF NOT EXISTS safe_zones (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL, -- HOME, CAMPUS, WORKPLACE, TRANSIT_HUB
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    radius_meters INTEGER DEFAULT 300 NOT NULL,
    curfew_start VARCHAR(10) DEFAULT '22:00',
    curfew_end VARCHAR(10) DEFAULT '06:00',
    is_curfew_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================================================================
-- 12. ADMIN_USERS & AUDIT_LOGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS admin_users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(32) DEFAULT 'OPERATOR' NOT NULL, -- SUPERADMIN, DISPATCHER, OPERATOR
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    actor_type VARCHAR(32) NOT NULL, -- USER, GUARDIAN, ADMIN, SYSTEM
    actor_id VARCHAR(36) NULL,
    action VARCHAR(64) NOT NULL,
    resource VARCHAR(64) NOT NULL,
    resource_id VARCHAR(64) NULL,
    details JSONB NULL,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(255) NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);

-- ============================================================================
-- 13. DEVICE_TOKENS & REFRESH_TOKENS
-- ============================================================================
CREATE TABLE IF NOT EXISTS device_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NULL REFERENCES users(id) ON DELETE CASCADE,
    guardian_id VARCHAR(36) NULL REFERENCES guardians(id) ON DELETE CASCADE,
    token_value VARCHAR(255) NOT NULL UNIQUE,
    device_type VARCHAR(32) DEFAULT 'ANDROID',
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NULL,
    guardian_id VARCHAR(36) NULL,
    admin_id VARCHAR(36) NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
