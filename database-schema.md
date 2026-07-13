# 🗄️ SafeRoute Saheli Database Schema

> **PostgreSQL normalized schema for secure incident documentation and user management**

---

## 📐 **1. Design Principles**

✅ **Normalization (3NF):** Reduce data redundancy  
✅ **Media Separation:** S3 for files, PostgreSQL for metadata  
✅ **Audit Trails:** Every admin action logged with timestamp & actor  
✅ **Soft Deletes:** Users, incidents archived (never hard-deleted)  
✅ **Encrypted Sensitive Fields:** Passwords, API keys, tokens  
✅ **Indexed Query Paths:** Frequent WHERE clauses indexed for speed  
✅ **Foreign Key Constraints:** Referential integrity enforced at DB level  

---

## 📋 **2. Entity-Relationship Diagram**

```
users (1) ─────────┬─────────→ user_profiles
          │       │
          │       ├─────────→ device_pairings (M) ──→ devices
          │       │
          │       ├─────────→ contacts (M) ──→ emergency_contacts
          │       │
          │       ├─────────→ trips (M) ──→ trip_points (M)
          │       │
          │       ├─────────→ alerts (M) ──────┐
          │       │                            ↓
          │       │                         incidents (1)
          │       │                            ↓
          │       │                         evidence (M)
          │       │                            ↓
          │       │                         ai_scores (M)
          │       │
          │       ├─────────→ abuse_reports (M)
          │       │
          │       └─────────→ notifications (M)
          │
          └─────────→ user_roles (M) ──→ roles
                                        (user, guardian, operator, admin)

admin_actions ← admin_users (subset of users with admin role)
audit_logs ← all tables (tracks all changes)
```

---

## 🔑 **3. Core Tables
### 👤 **users** (Authentication & User Accounts)

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  last_login_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
```

**Purpose:** User authentication, email verification, password reset  
**Security:** Password hashed with bcrypt (12 rounds), never logged

---

### 👤 **user_profiles** (Extended User Information)

```sql
CREATE TABLE user_profiles (
  id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  gender VARCHAR(50),
  age_group VARCHAR(50),
  emergency_address VARCHAR(500),
  city VARCHAR(100),
  state VARCHAR(100),
  country VARCHAR(100),
  preferences_json JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Preferences JSON Example:**
```json
{
  "language": "en",
  "notification_sound": true,
  "dark_mode": false,
  "trip_auto_start": false
}
```

---

### 🔐 **roles** (Role Definitions)

```sql
CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  role_name VARCHAR(50) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO roles (role_name, description) VALUES
('user', 'Regular app user (self data access)'),
('guardian', 'Trusted emergency contact (view assigned users)'),
('operator', 'Emergency responder (view all incidents, assign cases)'),
('admin', 'System administrator (user mgmt, reports)'),
('super_admin', 'Infrastructure admin (system config, secrets)');
```

---

### 🎯 **user_roles** (Role Assignments)

```sql
CREATE TABLE user_roles (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  assigned_by INTEGER REFERENCES users(id),
  assigned_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
```

### 📟 **devices** (Wearable Device Inventory)

```sql
CREATE TABLE devices (
  id SERIAL PRIMARY KEY,
  device_uuid VARCHAR(36) UNIQUE NOT NULL,
  device_type VARCHAR(50),  -- 'ESP32-S3', 'ESP32-CAM', etc.
  hardware_model VARCHAR(100),
  firmware_version VARCHAR(20),
  battery_level INTEGER,  -- 0-100%
  status VARCHAR(50),  -- 'active', 'inactive', 'lost', 'revoked'
  last_seen_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_devices_uuid ON devices(device_uuid);
CREATE INDEX idx_devices_status ON devices(status);
```

---

### 🔗 **device_pairings** (User-Device Relationships)

```sql
CREATE TABLE device_pairings (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  pairing_status VARCHAR(50),  -- 'paired', 'unpaired', 'lost'
  ble_public_key VARCHAR(255),  -- ECDH public key for pairing
  paired_at TIMESTAMP DEFAULT NOW(),
  unpaired_at TIMESTAMP,
  UNIQUE(user_id, device_id)
);

CREATE INDEX idx_device_pairings_user_id ON device_pairings(user_id);
```

---

### 👥 **contacts** (Contact Directory)

```sql
CREATE TABLE contacts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  contact_name VARCHAR(255) NOT NULL,
  contact_phone VARCHAR(20),
  contact_email VARCHAR(255),
  contact_type VARCHAR(50),  -- 'friend', 'family', 'emergency_service'
  is_trusted_guardian BOOLEAN DEFAULT FALSE,
  relationship VARCHAR(50),  -- 'mother', 'friend', 'colleague', etc.
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contacts_user_id ON contacts(user_id);
```

---

### 📞 **emergency_contacts** (Escalation Preferences)

```sql
CREATE TABLE emergency_contacts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
  priority_order INTEGER,  -- 1 = highest priority
  notify_push BOOLEAN DEFAULT TRUE,
  notify_sms BOOLEAN DEFAULT TRUE,
  notify_call BOOLEAN DEFAULT FALSE,
  notify_whatsapp BOOLEAN DEFAULT FALSE,
  can_view_location BOOLEAN DEFAULT TRUE,
  can_escalate_incident BOOLEAN DEFAULT FALSE,
  UNIQUE(user_id, contact_id)
);
```

### 🚗 **trips** (Trip Sessions)

```sql
CREATE TABLE trips (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  trip_name VARCHAR(255),
  start_location VARCHAR(255),
  end_location VARCHAR(255),
  start_lat DECIMAL(10, 8),
  start_lng DECIMAL(11, 8),
  end_lat DECIMAL(10, 8),
  end_lng DECIMAL(11, 8),
  trip_status VARCHAR(50),  -- 'active', 'completed', 'cancelled'
  risk_score INTEGER,  -- 0-100
  started_at TIMESTAMP DEFAULT NOW(),
  ended_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_status ON trips(trip_status);
```

---

### 📍 **trip_points** (GPS Breadcrumb Trail)

```sql
CREATE TABLE trip_points (
  id SERIAL PRIMARY KEY,
  trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  altitude DECIMAL(10, 2),
  speed DECIMAL(5, 2),  -- m/s
  heading DECIMAL(5, 2),  -- 0-360 degrees
  accuracy DECIMAL(5, 2),  -- GPS accuracy in meters
  captured_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trip_points_trip_id ON trip_points(trip_id);
CREATE INDEX idx_trip_points_location ON trip_points USING GIST (ll_to_earth(latitude, longitude));
```

---

### 🚨 **alerts** (Emergency Alert Events)

```sql
CREATE TABLE alerts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  trip_id INTEGER REFERENCES trips(id),
  device_id INTEGER REFERENCES devices(id),
  alert_type VARCHAR(50),  -- 'SOS', 'silent_SOS', 'motion_anomaly', 'route_risk'
  severity VARCHAR(50),  -- 'low', 'medium', 'high', 'critical'
  trigger_source VARCHAR(50),  -- 'button', 'voice', 'ai_detection'
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  status VARCHAR(50),  -- 'triggered', 'escalated', 'resolved', 'cancelled'
  created_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP
);

CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_status ON alerts(status);
```

---

### 🎯 **incidents** (Full Incident Records)

```sql
CREATE TABLE incidents (
  id SERIAL PRIMARY KEY,
  alert_id INTEGER NOT NULL UNIQUE REFERENCES alerts(id),
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255),
  summary TEXT,
  incident_type VARCHAR(50),  -- 'physical_threat', 'digital_abuse', 'other'
  severity VARCHAR(50),  -- 'low', 'medium', 'high', 'critical'
  location_lat DECIMAL(10, 8),
  location_lng DECIMAL(11, 8),
  incident_status VARCHAR(50),  -- 'open', 'assigned', 'resolved', 'archived'
  assigned_to INTEGER REFERENCES users(id),  -- operator/admin
  user_notes TEXT,
  admin_notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_incidents_user_id ON incidents(user_id);
CREATE INDEX idx_incidents_status ON incidents(incident_status);
CREATE INDEX idx_incidents_assigned_to ON incidents(assigned_to);
```

### 📸 **evidence** (Media Metadata - Files Stored in S3)

```sql
CREATE TABLE evidence (
  id SERIAL PRIMARY KEY,
  incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
  media_type VARCHAR(50),  -- 'image', 'audio', 'video'
  file_name VARCHAR(255),
  s3_key VARCHAR(255),  -- path in S3 bucket
  s3_bucket VARCHAR(255),  -- bucket name
  file_size_bytes INTEGER,
  file_hash_sha256 VARCHAR(64),  -- for integrity verification
  captured_at TIMESTAMP,
  upload_status VARCHAR(50),  -- 'pending', 'uploading', 'success', 'failed'
  access_level VARCHAR(50),  -- 'responder_only', 'admin', 'public'
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_evidence_incident_id ON evidence(incident_id);
CREATE INDEX idx_evidence_upload_status ON evidence(upload_status);
```

**Note:** Media stored in encrypted S3 bucket, PostgreSQL holds only metadata

---

### 🛡️ **abuse_reports** (Digital Abuse Documentation)

```sql
CREATE TABLE abuse_reports (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category VARCHAR(50),  -- 'harassment', 'threat', 'impersonation', 'blackmail', 'obscene'
  platform_name VARCHAR(100),  -- 'instagram', 'facebook', 'twitter', 'whatsapp', 'email'
  report_text TEXT,
  source_link VARCHAR(500),
  screenshot_id INTEGER REFERENCES evidence(id),
  severity VARCHAR(50),  -- 'low', 'medium', 'high', 'critical'
  reporter_name VARCHAR(255),  -- person doing abuse
  reporter_account VARCHAR(255),
  report_status VARCHAR(50),  -- 'draft', 'submitted', 'reviewed'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_abuse_reports_user_id ON abuse_reports(user_id);
CREATE INDEX idx_abuse_reports_category ON abuse_reports(category);
```

---

### 🤖 **ai_scores** (ML Model Inference Results)

```sql
CREATE TABLE ai_scores (
  id SERIAL PRIMARY KEY,
  incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
  score_type VARCHAR(50),  -- 'route_risk', 'stalking_risk', 'threat_level'
  score_value DECIMAL(5, 2),  -- 0.0 to 100.0
  confidence DECIMAL(5, 2),  -- 0.0 to 1.0 (how sure is the model)
  model_version VARCHAR(50),  -- v1.2.3 for reproducibility
  explanation_json JSONB,  -- why did the model decide this?
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ai_scores_incident_id ON ai_scores(incident_id);
```

**Explanation JSON Example:**
```json
{
  "signals": [
    {"signal": "route_similarity", "weight": 0.3, "value": 0.85},
    {"signal": "time_context", "weight": 0.2, "value": 1.0},
    {"signal": "repeat_pattern", "weight": 0.5, "value": 0.72}
  ],
  "final_score": 82.5,
  "recommendation": "medium_confidence_alert"
}
```

---

### 📧 **notifications** (Delivery Tracking)

```sql
CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  alert_id INTEGER REFERENCES alerts(id),
  channel VARCHAR(50),  -- 'push', 'sms', 'email', 'call'
  recipient VARCHAR(255),  -- phone number or email
  message TEXT,
  status VARCHAR(50),  -- 'pending', 'sent', 'delivered', 'failed'
  error_message TEXT,
  sent_at TIMESTAMP,
  delivered_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
```

---

### 📋 **admin_logs** (Admin Action Audit Trail)

```sql
CREATE TABLE admin_logs (
  id SERIAL PRIMARY KEY,
  admin_user_id INTEGER NOT NULL REFERENCES users(id),
  action_type VARCHAR(100),  -- 'user_created', 'incident_resolved', 'evidence_accessed'
  target_type VARCHAR(50),  -- 'user', 'incident', 'evidence'
  target_id INTEGER,
  action_details JSONB,
  ip_address VARCHAR(50),
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_admin_logs_admin_user_id ON admin_logs(admin_user_id);
CREATE INDEX idx_admin_logs_action_type ON admin_logs(action_type);
```

---

### 🔐 **audit_logs** (Complete Change History)

```sql
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  actor_id INTEGER REFERENCES users(id),
  actor_role VARCHAR(50),
  action VARCHAR(50),  -- 'create', 'update', 'delete', 'view'
  resource_type VARCHAR(50),  -- 'user', 'incident', 'evidence', 'contact'
  resource_id INTEGER,
  old_value_json JSONB,  -- before update
  new_value_json JSONB,  -- after update
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_actor_id ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
```

---

## 📊 **4. Entity Relationships**

### **User Relationships**
- 1 User → M Device_Pairings (user has many wearables)
- 1 User → M Contacts (user has emergency contacts)
- 1 User → M Trips (user creates many trips)
- 1 User → M Alerts (user generates alerts)
- 1 User → M Incidents (user involved in incidents)
- 1 User → M Abuse_Reports (user reports abuse)
- 1 User → M Notifications (user receives notifications)
- 1 User → M User_Roles (user can have multiple roles)

### **Trip Relationships**
- 1 Trip → M Trip_Points (trip has many GPS locations)
- 1 Trip → 1 Alert (trip generates alert on emergency)

### **Incident Relationships**
- 1 Alert → 1 Incident (alert spawns incident)
- 1 Incident → M Evidence (incident has multiple media)
- 1 Incident → M AI_Scores (multiple ML models score incident)

### **Cascading Deletes**
- Delete User → soft delete (mark as deleted, keep audit)
- Delete Incident → soft delete (archive, keep for compliance)
- Delete Evidence → delete S3 file + DB record (after 90 days)

---

## 💾 **5. Storage Architecture**

### **PostgreSQL Responsibilities**
✅ User authentication & profiles  
✅ Device pairings & metadata  
✅ Location history (trip points)  
✅ Incident records & status  
✅ Evidence *metadata* (not files)  
✅ Audit trails (immutable)  
✅ Relationships & constraints  

### **S3 Object Storage Responsibilities**
✅ Image files (JPEG, PNG - max 50MB)  
✅ Audio files (M4A, WAV - max 100MB)  
✅ Video clips (MP4 - max 500MB)  
✅ Encrypted with AES-256  
✅ Versioning enabled (immutable evidence)  
✅ Lifecycle policy: delete after 90 days  

### **Metadata-Only in PostgreSQL**
```json
{
  "id": 123,
  "incident_id": 456,
  "media_type": "image",
  "file_name": "incident_photo_20260713_153000.jpg",
  "s3_key": "incidents/456/photo_1234567890.jpg",
  "s3_bucket": "saferoute-evidence",
  "file_size_bytes": 2500000,
  "file_hash_sha256": "abcd1234...",
  "captured_at": "2026-07-13T15:30:00Z",
  "upload_status": "success",
  "access_level": "responder_only"
}
```

### **Access Control on Evidence**
1. **Authentication:** JWT token must be valid
2. **Authorization:** User role must be responder, operator, or admin
3. **Incident Assignment:** User must be assigned to incident
4. **Audit Log:** Entry created before download
5. **Expiry:** Signed URL expires after 1 hour
6. **Rate Limiting:** Max 10 downloads per hour

---

## 🔐 **6. Data Retention Policy**

| Data Type | Retention | Reason | Action |
|---|---|---|---|
| User Profile | Forever (soft delete) | Historical records | Mark deleted, keep audit |
| Evidence Files | 90 days (default) | Compliance, storage cost | Auto-delete from S3 |
| Evidence Metadata | Forever | Incident history | Retain in PostgreSQL |
| Trip Points | 30 days | Location privacy | Auto-archive then delete |
| Audit Logs | Forever | Compliance, legal hold | Immutable, append-only |
| Notifications | 90 days | Support reference | Auto-delete |
| Error Logs | 7 days | Debugging | Auto-purge |

---

## 🚀 **7. Performance Optimization**

### **Indexes for Query Speed**

| Index | Purpose | Benefit |
|---|---|---|
| `idx_users_email` | Login by email | O(log n) instead of O(n) |
| `idx_trips_user_id` | Get user's trips | Fast filtering |
| `idx_incidents_status` | Dashboard counts | Pre-grouped by status |
| `idx_alert_created_at` | Time-range queries | Recent incidents first |
| `idx_trip_points_location` | Geospatial queries | PostGIS nearest-neighbor |

### **Query Patterns**

```sql
-- Dashboard: All open incidents in real-time
SELECT * FROM incidents 
WHERE incident_status = 'open' 
ORDER BY created_at DESC LIMIT 50;

-- User: Get my latest trip with risk score
SELECT t.*, COUNT(tp.id) as point_count
FROM trips t
LEFT JOIN trip_points tp ON t.id = tp.trip_id
WHERE t.user_id = $1
ORDER BY t.started_at DESC LIMIT 1;

-- Geospatial: Incidents near user location
SELECT * FROM incidents
WHERE earth_distance(ll_to_earth(latitude, longitude),
                     ll_to_earth($1, $2)) < 5000  -- within 5km
ORDER BY earth_distance(...) LIMIT 10;
```

---

## ✅ **8. Data Integrity Constraints**

```sql
-- Foreign keys enforce relationships
ALTER TABLE user_profiles ADD CONSTRAINT fk_user_profiles_user_id
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Unique constraints prevent duplicates
ALTER TABLE device_pairings ADD UNIQUE(user_id, device_id);

-- Check constraints enforce valid values
ALTER TABLE evidence ADD CONSTRAINT check_valid_media_type
  CHECK (media_type IN ('image', 'audio', 'video'));

ALTER TABLE incidents ADD CONSTRAINT check_valid_severity
  CHECK (severity IN ('low', 'medium', 'high', 'critical'));

-- Not null constraints ensure required fields
ALTER TABLE alerts ALTER COLUMN alert_type SET NOT NULL;
ALTER TABLE alerts ALTER COLUMN severity SET NOT NULL;
```

---

**Schema Version:** 1.0  
**Last Updated:** 2026-07-13  
**Database:** PostgreSQL 14+  
**Object Storage:** AWS S3 or MinIO