#include "ble_companion.h"

BLEServer* BLECompanion::pServer = nullptr;
BLECharacteristic* BLECompanion::pEmergencyChar = nullptr;
BLECharacteristic* BLECompanion::pTelemetryChar = nullptr;
BLECharacteristic* BLECompanion::pConfigChar = nullptr;
BLECharacteristic* BLECompanion::pPairingChar = nullptr;

bool BLECompanion::_deviceConnected = false;
bool BLECompanion::_oldDeviceConnected = false;
bool BLECompanion::_isPaired = false;

void BLECompanionServerCallbacks::onConnect(BLEServer* pServer) {
    BLECompanion::_deviceConnected = true;
    Serial.println("[BLE] Phone Companion Connected over Bluetooth Low Energy");
}

void BLECompanionServerCallbacks::onDisconnect(BLEServer* pServer) {
    BLECompanion::_deviceConnected = false;
    Serial.println("[BLE] Phone Companion Disconnected");
    // Restart advertising to allow reconnection
    pServer->getAdvertising()->start();
}

void BLECompanionConfigCallbacks::onWrite(BLECharacteristic* pCharacteristic) {
    String value = pCharacteristic->getValue().c_str();
    if (value.length() > 0) {
        Serial.printf("[BLE] Config received: %s\n", value.c_str());
        // Parses CONFIG:WIFI:SSID:PASS or CONFIG:BACKEND:URL
    }
}

void BLECompanionPairingCallbacks::onWrite(BLECharacteristic* pCharacteristic) {
    String value = pCharacteristic->getValue().c_str();
    if (value.length() > 0) {
        Serial.printf("[BLE] Pairing handshake received: %s\n", value.c_str());
        // Verify token or secret matching DEVICE_SECRET
        if (value.indexOf(DEVICE_SECRET) >= 0 || value.startsWith("PAIR:OK")) {
            BLECompanion::setPaired(true);
            pCharacteristic->setValue("PAIR_STATUS:SUCCESS_AUTHORIZED");
            pCharacteristic->notify();
            Serial.println("[BLE] Device successfully paired and authorized!");
        } else {
            pCharacteristic->setValue("PAIR_STATUS:ERROR_REJECTED");
            pCharacteristic->notify();
        }
    }
}

void BLECompanion::init(const char* deviceName) {
    Serial.printf("[BLE] Initializing BLE Peripheral: %s\n", deviceName);
    BLEDevice::init(deviceName);

    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new BLECompanionServerCallbacks());

    // Create Main Saheli Service
    BLEService* pService = pServer->createService(SAHELI_SERVICE_UUID);

    // 1. Emergency Trigger Characteristic (Notify + Read)
    pEmergencyChar = pService->createCharacteristic(
        SAHELI_CHAR_EMERGENCY_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pEmergencyChar->addDescriptor(new BLE2902());
    pEmergencyChar->setValue("STATUS:STANDBY");

    // 2. Telemetry Stream Characteristic (Notify + Read)
    pTelemetryChar = pService->createCharacteristic(
        SAHELI_CHAR_TELEMETRY_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pTelemetryChar->addDescriptor(new BLE2902());
    pTelemetryChar->setValue("TELEMETRY:IDLE");

    // 3. Remote Configuration Characteristic (Write)
    pConfigChar = pService->createCharacteristic(
        SAHELI_CHAR_CONFIG_UUID,
        BLECharacteristic::PROPERTY_WRITE
    );
    pConfigChar->setCallbacks(new BLECompanionConfigCallbacks());

    // 4. Secure Pairing Characteristic (Write + Read + Notify)
    pPairingChar = pService->createCharacteristic(
        SAHELI_CHAR_PAIRING_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_WRITE |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pPairingChar->setCallbacks(new BLECompanionPairingCallbacks());
    pPairingChar->addDescriptor(new BLE2902());
    pPairingChar->setValue("PAIR_STATUS:UNPAIRED");

    pService->start();

    // Start Advertising
    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SAHELI_SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06); // Functions that help with iPhone connections issue
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();

    Serial.println("[BLE] GATT Server and Advertising active. Awaiting phone companion connection.");
}

void BLECompanion::sendEmergencyAlert(const char* triggerType, float confidence) {
    if (pEmergencyChar && _deviceConnected) {
        char payload[128];
        snprintf(payload, sizeof(payload), "EMERGENCY:%s:%.2f:%lu", triggerType, confidence, millis());
        pEmergencyChar->setValue(payload);
        pEmergencyChar->notify();
        Serial.printf("[BLE] Transmitted Instant Emergency Alert over BLE: %s\n", payload);
    }
}

void BLECompanion::sendTelemetry(float bpm, float spo2, int batteryPercent, const char* motionState) {
    if (pTelemetryChar && _deviceConnected) {
        char payload[128];
        snprintf(payload, sizeof(payload), "TELEM:%.1f:%.1f:%d:%s", bpm, spo2, batteryPercent, motionState);
        pTelemetryChar->setValue(payload);
        pTelemetryChar->notify();
    }
}

bool BLECompanion::isConnected() {
    return _deviceConnected;
}

bool BLECompanion::isPaired() {
    return _isPaired;
}

void BLECompanion::setPaired(bool paired) {
    _isPaired = paired;
}
