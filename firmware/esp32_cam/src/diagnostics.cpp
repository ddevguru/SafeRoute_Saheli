#include "diagnostics.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "camera_driver.h"

void Diagnostics::sendHeartbeat() {
    if (WiFi.status() != WL_CONNECTED) {
        return;
    }

    HTTPClient http;
    String url = String(BACKEND_BASE_URL) + "/devices/heartbeat";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;
    doc["device_id"] = DEVICE_ID;
    doc["device_secret"] = DEVICE_SECRET;
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["camera_health"] = CameraDriver::isInitialized() ? "OK" : "ERROR";
    doc["firmware_version"] = FIRMWARE_VERSION;

    String body;
    serializeJson(doc, body);

    int code = http.POST(body);
    Serial.printf("[Diagnostics] Heartbeat to %s returned code %d\n", url.c_str(), code);
    http.end();
}

void Diagnostics::printDiagnostics() {
    Serial.println("\n--- ESP32-CAM DIAGNOSTICS ---");
    Serial.printf("Device ID:      %s\n", DEVICE_ID);
    Serial.printf("Firmware:       %s\n", FIRMWARE_VERSION);
    Serial.printf("WiFi Status:    %s (IP: %s, RSSI: %d dBm)\n", 
                  (WiFi.status() == WL_CONNECTED) ? "CONNECTED" : "DISCONNECTED",
                  WiFi.localIP().toString().c_str(), WiFi.RSSI());
    Serial.printf("Camera Sensor:  %s\n", CameraDriver::isInitialized() ? "OPERATIONAL" : "FAILED");
    Serial.printf("PSRAM:          %s (Free: %u bytes)\n", 
                  psramFound() ? "DETECTED" : "NONE", (unsigned int)CameraDriver::getFreePSRAM());
    Serial.printf("Heap Free:      %u bytes\n", (unsigned int)ESP.getFreeHeap());
    Serial.println("-----------------------------\n");
}

bool Diagnostics::isHealthy() {
    return (WiFi.status() == WL_CONNECTED) && CameraDriver::isInitialized();
}
