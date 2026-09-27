#include "backend_client.h"
#include <WiFi.h>

bool BackendClient::postJson(const String& endpoint, const JsonDocument& doc, String* responseOut) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.printf("[BackendClient] WiFi disconnected. Cannot POST to %s\n", endpoint.c_str());
        return false;
    }

    HTTPClient http;
    String fullUrl = String(BACKEND_BASE_URL) + endpoint;
    http.begin(fullUrl);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(5000); // 5 seconds timeout

    String requestBody;
    serializeJson(doc, requestBody);

    int httpCode = http.POST(requestBody);
    bool success = (httpCode >= 200 && httpCode < 300);

    if (success) {
        if (responseOut) {
            *responseOut = http.getString();
        }
    } else {
        Serial.printf("[BackendClient] POST %s failed. Code: %d, Response: %s\n", 
                      endpoint.c_str(), httpCode, http.getString().c_str());
    }

    http.end();
    return success;
}

bool BackendClient::sendHeartbeat(int batteryPercent, float batteryVoltage, int rssi) {
    StaticJsonDocument<256> doc;
    doc["device_id"] = DEVICE_ID;
    doc["device_secret"] = DEVICE_SECRET;
    doc["battery_percent"] = batteryPercent;
    doc["battery_voltage"] = batteryVoltage;
    doc["wifi_rssi"] = rssi;
    doc["firmware_version"] = FIRMWARE_VERSION;

    Serial.printf("[BackendClient] Sending Heartbeat (Batt: %d%%, %.2fV, RSSI: %d)...\n", 
                  batteryPercent, batteryVoltage, rssi);
    return postJson("/devices/heartbeat", doc);
}

bool BackendClient::sendEmergency(const String& triggerType, double latitude, double longitude, int batteryPercent, float confidence) {
    StaticJsonDocument<384> doc;
    doc["device_id"] = DEVICE_ID;
    doc["device_secret"] = DEVICE_SECRET;
    doc["trigger_type"] = triggerType;
    doc["latitude"] = latitude;
    doc["longitude"] = longitude;
    doc["battery_percent"] = batteryPercent;
    doc["confidence"] = confidence;

    Serial.printf("[BackendClient] SENDING SOS TRIGGER: %s at [%.6f, %.6f]!\n", 
                  triggerType.c_str(), latitude, longitude);

    bool ok = postJson("/emergency/trigger", doc);
    if (!ok) {
        Serial.println("[BackendClient] SOS direct transmission failed. Queuing into offline SPIFFS flash storage!");
        QueuedEmergency qe;
        qe.triggerType = triggerType;
        qe.latitude = latitude;
        qe.longitude = longitude;
        qe.batteryPercent = batteryPercent;
        qe.timestamp = millis() / 1000;
        LocalStorage::queueEmergency(qe);
    }
    return ok;
}

bool BackendClient::sendSensorEvent(const String& eventType, const JsonDocument& payload) {
    StaticJsonDocument<512> doc;
    doc["device_id"] = DEVICE_ID;
    doc["device_secret"] = DEVICE_SECRET;
    doc["event_type"] = eventType;
    doc["payload"] = payload;

    return postJson("/devices/events", doc);
}

void BackendClient::flushOfflineQueue() {
    if (WiFi.status() != WL_CONNECTED || !LocalStorage::hasQueuedEvents()) {
        return;
    }

    QueuedEmergency events[10];
    size_t count = LocalStorage::getQueuedEvents(events, 10);
    if (count == 0) return;

    Serial.printf("[BackendClient] Flushing %d offline queued SOS events to server...\n", count);
    size_t sentCount = 0;

    for (size_t i = 0; i < count; i++) {
        StaticJsonDocument<384> doc;
        doc["device_id"] = DEVICE_ID;
        doc["device_secret"] = DEVICE_SECRET;
        doc["trigger_type"] = events[i].triggerType + "_OFFLINE_REPLAY";
        doc["latitude"] = events[i].latitude;
        doc["longitude"] = events[i].longitude;
        doc["battery_percent"] = events[i].batteryPercent;
        doc["confidence"] = 1.0;

        if (postJson("/emergency/trigger", doc)) {
            sentCount++;
        } else {
            Serial.println("[BackendClient] Offline replay failed mid-flush. Will retry next cycle.");
            break;
        }
    }

    if (sentCount == count) {
        Serial.println("[BackendClient] All offline events successfully synced! Clearing local queue.");
        LocalStorage::clearQueue();
    }
}
