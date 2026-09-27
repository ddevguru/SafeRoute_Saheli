#include "wifi_manager.h"

unsigned long WiFiManager::lastReconnectAttempt = 0;

void WiFiManager::init() {
    Serial.println("[WiFi] Initializing WiFi Subsystem...");
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false); // Disable WiFi power saving for ultra-low latency emergency reporting
    
    Serial.printf("[WiFi] Connecting to SSID: %s\n", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    // Non-blocking initial attempt
    lastReconnectAttempt = millis();
}

void WiFiManager::maintainConnection() {
    if (WiFi.status() == WL_CONNECTED) {
        return;
    }
    
    unsigned long now = millis();
    if (now - lastReconnectAttempt >= RECONNECT_INTERVAL_MS) {
        lastReconnectAttempt = now;
        Serial.println("[WiFi] Connection lost or not established. Reconnecting...");
        WiFi.disconnect();
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    }
}

bool WiFiManager::isConnected() {
    return (WiFi.status() == WL_CONNECTED);
}

int WiFiManager::getRSSI() {
    if (isConnected()) {
        return WiFi.RSSI();
    }
    return -999;
}

String WiFiManager::getIPAddress() {
    if (isConnected()) {
        return WiFi.localIP().toString();
    }
    return "0.0.0.0";
}

String WiFiManager::getMacAddress() {
    return WiFi.macAddress();
}
