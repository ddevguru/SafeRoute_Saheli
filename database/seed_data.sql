-- SafeRoute Saheli Initial Seed Data
USE saferoute_saheli;

-- Default Admin User (Password: SaheliAdmin@2026 bcrypt hash)
-- Generated with bcrypt salt 12
INSERT INTO admin_users (id, username, email, password_hash, role, is_active)
VALUES (
    'adm-00000001-0000-0000-0000-000000000001',
    'saheli_admin',
    'admin@saheli.safe',
    '$2b$12$6GqFf.9hK6wX5Z4V8yD0Iu897W5Z1v6i3g6o7p4b0h9i1j2k3l4m5',
    'SUPERADMIN',
    TRUE
) ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- Safe Places (Verified Police Stations, Hospitals, 24x7 Help Centers)
INSERT INTO safe_places (id, name, category, latitude, longitude, address, phone_number, is_24x7, verified_status)
VALUES
('sp-pol-001', 'Central Women Police Assistance Booth', 'POLICE', 28.613939, 77.209021, 'Connaught Place Circle, New Delhi', '+911123456789', TRUE, TRUE),
('sp-pol-002', 'Metro Security Police Station', 'POLICE', 28.628900, 77.207500, 'Barakhamba Road Metro Station, Gate 2', '+911123456790', TRUE, TRUE),
('sp-hosp-001', 'City General Multi-Specialty Hospital', 'HOSPITAL', 28.618900, 77.215500, 'Ashoka Road, New Delhi', '+911145678901', TRUE, TRUE),
('sp-hosp-002', 'St. Mary 24x7 Emergency Care Center', 'HOSPITAL', 28.605000, 77.201000, 'Chanakyapuri Safe Corridor, New Delhi', '+911145678902', TRUE, TRUE),
('sp-pharma-001', 'Apollo 24x7 Emergency Chemist', 'PHARMACY', 28.621000, 77.210000, 'Janpath Lane 4, New Delhi', '+911145678903', TRUE, TRUE),
('sp-shelter-001', 'One Stop Crisis Center (Sakhi Center)', 'SHELTER', 28.610500, 77.220000, 'India Gate Northern Precinct, New Delhi', '181', TRUE, TRUE);

-- Synthetic Spatial Risk Benchmark Features (Used by Neuro-Fuzzy & GA models)
INSERT INTO risk_features (latitude, longitude, radius_meters, crime_rate, lighting_quality, isolation_index, crowd_density, police_proximity_meters, hospital_proximity_meters, historical_incident_count, data_source_label)
VALUES
(28.6139, 77.2090, 250.0, 0.15, 0.90, 0.10, 0.85, 120.0, 450.0, 2, 'SYNTHETIC_BENCHMARK'),
(28.6200, 77.2150, 300.0, 0.20, 0.85, 0.20, 0.75, 300.0, 200.0, 3, 'SYNTHETIC_BENCHMARK'),
(28.6280, 77.2020, 350.0, 0.45, 0.40, 0.70, 0.25, 1200.0, 1800.0, 12, 'SYNTHETIC_BENCHMARK'),
(28.6050, 77.2250, 400.0, 0.65, 0.25, 0.85, 0.10, 2100.0, 2400.0, 19, 'SYNTHETIC_BENCHMARK');
