#ifndef SAHELI_BLE_COMPANION_H
#define SAHELI_BLE_COMPANION_H

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "../config.h"

// SafeRoute Saheli Standard BLE UUIDs
#define SAHELI_SERVICE_UUID           "00005A48-0000-1000-8000-00805F9B34FB"
#define SAHELI_CHAR_EMERGENCY_UUID    "00005A49-0000-1000-8000-00805F9B34FB"
#define SAHELI_CHAR_TELEMETRY_UUID    "00005A4A-0000-1000-8000-00805F9B34FB"
#define SAHELI_CHAR_CONFIG_UUID       "00005A4B-0000-1000-8000-00805F9B34FB"
#define SAHELI_CHAR_PAIRING_UUID      "00005A4C-0000-1000-8000-00805F9B34FB"

class BLECompanionServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override;
    void onDisconnect(BLEServer* pServer) override;
};

class BLECompanionConfigCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pCharacteristic) override;
};

class BLECompanionPairingCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pCharacteristic) override;
};

class BLECompanion {
public:
    static void init(const char* deviceName = "Saheli-Wearable-001");
    static void sendEmergencyAlert(const char* triggerType, float confidence = 1.0f);
    static void sendTelemetry(float bpm, float spo2, int batteryPercent, const char* motionState);
    static bool isConnected();
    static bool isPaired();
    static void setPaired(bool paired);

    static BLECharacteristic* pEmergencyChar;
    static BLECharacteristic* pTelemetryChar;
    static BLECharacteristic* pConfigChar;
    static BLECharacteristic* pPairingChar;

private:
    static bool _deviceConnected;
    static bool _oldDeviceConnected;
    static bool _isPaired;
    static BLEServer* pServer;

    friend class BLECompanionServerCallbacks;
};

#endif // SAHELI_BLE_COMPANION_H
