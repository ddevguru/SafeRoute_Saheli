#ifndef SAHELI_BACKEND_CLIENT_H
#define SAHELI_BACKEND_CLIENT_H

#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "../config.h"
#include "../storage/local_storage.h"

class BackendClient {
public:
    static bool sendHeartbeat(int batteryPercent, float batteryVoltage, int rssi);
    static bool sendEmergency(const String& triggerType, double latitude, double longitude, int batteryPercent, float confidence = 1.0f);
    static bool sendSensorEvent(const String& eventType, const JsonDocument& payload);
    static void flushOfflineQueue();

private:
    static bool postJson(const String& endpoint, const JsonDocument& doc, String* responseOut = nullptr);
};

#endif // SAHELI_BACKEND_CLIENT_H
