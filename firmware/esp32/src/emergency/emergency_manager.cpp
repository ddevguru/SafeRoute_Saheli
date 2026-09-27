#include "emergency_manager.h"
#include "../api/backend_client.h"

EmergencyState EmergencyManager::currentState = STATE_IDLE;
unsigned long EmergencyManager::alarmStartTime = 0;
unsigned long EmergencyManager::lastTriggerTime = 0;
String EmergencyManager::activeTriggerSource = "NONE";

Actuators* EmergencyManager::_actuators = nullptr;
GPSSensor* EmergencyManager::_gps = nullptr;
BatteryMonitor* EmergencyManager::_battery = nullptr;

void EmergencyManager::init(Actuators* actuators, GPSSensor* gps, BatteryMonitor* battery) {
    _actuators = actuators;
    _gps = gps;
    _battery = battery;
    currentState = STATE_IDLE;
    alarmStartTime = 0;
    lastTriggerTime = 0;
    activeTriggerSource = "NONE";
    Serial.println("[EmergencyManager] Initialized in IDLE state.");
}

void EmergencyManager::triggerEmergency(const String& triggerSource, float confidence) {
    unsigned long now = millis();
    if (currentState == STATE_ACTIVE_ALARM && (now - lastTriggerTime < 5000)) {
        Serial.printf("[EmergencyManager] Duplicate trigger ignored (%s)\n", triggerSource.c_str());
        return;
    }

    currentState = STATE_ACTIVE_ALARM;
    alarmStartTime = now;
    lastTriggerTime = now;
    activeTriggerSource = triggerSource;

    Serial.printf("\n======================================================\n");
    Serial.printf("[EMERGENCY TRIGGERED] SOURCE: %s | CONFIDENCE: %.2f\n", triggerSource.c_str(), confidence);
    Serial.printf("======================================================\n");

    // 1. Activate onboard alarms (Buzzer + Vibration)
    if (_actuators) {
        _actuators->setAlarmState(true);
    }

    // 2. Fetch Location Coordinates
    double lat = 28.6139; // Safe default / last known location if searching for satellites
    double lon = 77.2090;
    if (_gps && _gps->hasValidFix()) {
        GPSLocation loc = _gps->getLocation();
        lat = loc.latitude;
        lon = loc.longitude;
        Serial.printf("[EmergencyManager] Accurate GPS Fix: [%.6f, %.6f], Sats: %d\n", lat, lon, loc.satellites);
    } else {
        Serial.println("[EmergencyManager] Warning: GPS searching for satellite fix. Using last known/default location.");
    }

    // 3. Fetch Battery Level
    int batteryPct = 100;
    if (_battery) {
        batteryPct = _battery->readPercentage();
    }

    // 4. Send Instant SOS to SafeRoute Saheli Backend
    BackendClient::sendEmergency(triggerSource, lat, lon, batteryPct, confidence);
}

void EmergencyManager::update() {
    if (currentState == STATE_ACTIVE_ALARM) {
        if (_actuators) {
            _actuators->update();
        }

        if (millis() - alarmStartTime >= EMERGENCY_ALARM_DURATION_MS) {
            Serial.println("[EmergencyManager] Alarm duration reached timeout. Entering cooldown.");
            if (_actuators) {
                _actuators->setAlarmState(false);
            }
            currentState = STATE_COOLDOWN;
            lastTriggerTime = millis();
        }
    } else if (currentState == STATE_COOLDOWN) {
        if (millis() - lastTriggerTime >= 5000) {
            currentState = STATE_IDLE;
            Serial.println("[EmergencyManager] Cooldown ended. Ready for next trigger.");
        }
    }
}

bool EmergencyManager::isEmergencyActive() {
    return (currentState == STATE_ACTIVE_ALARM);
}

EmergencyState EmergencyManager::getState() {
    return currentState;
}

void EmergencyManager::cancelEmergency() {
    Serial.println("[EmergencyManager] Emergency explicitly canceled.");
    if (_actuators) {
        _actuators->setAlarmState(false);
    }
    currentState = STATE_IDLE;
}
