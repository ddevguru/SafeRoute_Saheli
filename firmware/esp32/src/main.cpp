#include <Arduino.h>
#include "config.h"
#include "sensors/touch_sensor.h"
#include "sensors/mpu6050.h"
#include "sensors/gps.h"
#include "sensors/microphone.h"
#include "sensors/battery.h"
#include "sensors/actuators.h"
#include "storage/local_storage.h"
#include "communication/wifi_manager.h"
#include "api/backend_client.h"
#include "emergency/emergency_manager.h"

// Hardware instances
TouchSensor touchSensor(PIN_TOUCH_SENSOR, TOUCH_HOLD_TRIGGER_MS);
MPU6050Sensor mpuSensor(PIN_I2C_SDA, PIN_I2C_SCL);
GPSSensor gpsSensor(PIN_GPS_RX, PIN_GPS_TX, GPS_BAUD_RATE);
MicrophoneSensor micSensor(PIN_I2S_SCK, PIN_I2S_WS, PIN_I2S_SD);
BatteryMonitor batteryMonitor(PIN_BATTERY_ADC, BATTERY_ADC_DIVIDER);
Actuators actuators(PIN_BUZZER, PIN_VIBRATION_MOSFET, PIN_STATUS_LED);

// Task handles
TaskHandle_t audioTaskHandle = NULL;
TaskHandle_t supervisorTaskHandle = NULL;

// Telemetry timers
unsigned long lastHeartbeatTime = 0;
unsigned long lastGpsPushTime = 0;

/**
 * FreeRTOS Core 0 Task: Continuous High-Speed I2S Microphone Stream
 * Dedicated solely to audio DSP to prevent missing acoustic clap spikes.
 */
void audioTask(void* parameter) {
    Serial.println("[Core 0] Audio Processing Task Started.");
    while (true) {
        if (micSensor.updateClapDetection()) {
            Serial.println("[AudioTask] 3-CLAP EMERGENCY PATTERN DETECTED!");
            EmergencyManager::triggerEmergency("CLAP", 0.95f);
        }
        vTaskDelay(pdMS_TO_TICKS(5)); // High temporal resolution
    }
}

/**
 * FreeRTOS Core 1 Task: System Supervisor, Sensor Poller & Network Handler
 */
void supervisorTask(void* parameter) {
    Serial.println("[Core 1] Supervisor Task Started.");
    while (true) {
        unsigned long currentMillis = millis();

        // 1. Maintain WiFi Connection
        WiFiManager::maintainConnection();

        // 2. Poll GPS NMEA Stream
        gpsSensor.update();

        // 3. Check Touch Sensor (1.5-second continuous hold)
        if (touchSensor.update()) {
            Serial.println("[Supervisor] TOUCH SENSOR SOS TRIGGERED!");
            EmergencyManager::triggerEmergency("TOUCH", 1.0f);
        }

        // 4. Poll 6-Axis Motion Sensor for Fall or Struggle
        MotionData motion = mpuSensor.read();
        if (motion.isFallDetected) {
            Serial.printf("[Supervisor] FALL DETECTED! Accel Mag: %.2f g\n", motion.accelMagnitude);
            EmergencyManager::triggerEmergency("MOTION_FALL", 0.90f);
        } else if (motion.isStruggleDetected) {
            Serial.printf("[Supervisor] PHYSICAL STRUGGLE DETECTED! Gyro Mag: %.2f dps\n", motion.gyroMagnitude);
            EmergencyManager::triggerEmergency("MOTION_STRUGGLE", 0.85f);
        }

        // 5. Update Emergency State Machine & Actuators
        EmergencyManager::update();

        // 6. Periodic Heartbeat & Telemetry Flush
        if (currentMillis - lastHeartbeatTime >= INTERVAL_HEARTBEAT_MS) {
            lastHeartbeatTime = currentMillis;
            int battPct = batteryMonitor.readPercentage();
            float battVolt = batteryMonitor.readVoltage();
            int rssi = WiFiManager::getRSSI();

            BackendClient::sendHeartbeat(battPct, battVolt, rssi);
            BackendClient::flushOfflineQueue();
        }

        // 7. Live GPS Tracking Push (Higher frequency if emergency is active)
        unsigned long gpsInterval = EmergencyManager::isEmergencyActive() 
                                    ? INTERVAL_EMERGENCY_GPS_MS 
                                    : INTERVAL_NORMAL_GPS_MS;

        if (currentMillis - lastGpsPushTime >= gpsInterval) {
            lastGpsPushTime = currentMillis;
            if (gpsSensor.hasValidFix() && WiFiManager::isConnected()) {
                GPSLocation loc = gpsSensor.getLocation();
                StaticJsonDocument<256> doc;
                doc["latitude"] = loc.latitude;
                doc["longitude"] = loc.longitude;
                doc["speed_kmph"] = loc.speedKmph;
                doc["accuracy_meters"] = loc.accuracyMeters;
                doc["satellites"] = loc.satellites;
                BackendClient::sendSensorEvent("GPS_TELEMETRY", doc);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(20)); // Yield 20ms
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n=======================================================");
    Serial.println("  SAFEROUTE SAHELI — WEARABLE SAFETY DEVICE FIRMWARE   ");
    Serial.printf ("  Firmware Version: %s | Device ID: %s\n", FIRMWARE_VERSION, DEVICE_ID);
    Serial.println("=======================================================");

    // 1. Initialize Actuators (Buzzer, Haptic, LED)
    actuators.begin();
    actuators.pulseVibration(200); // Startup tactile chime

    // 2. Initialize Touch Sensor
    touchSensor.begin();

    // 3. Initialize MPU6050
    if (!mpuSensor.begin()) {
        Serial.println("[Setup] Warning: MPU6050 initialization failed or not responding on I2C.");
    }

    // 4. Initialize GPS
    gpsSensor.begin();

    // 5. Initialize I2S Microphone
    if (!micSensor.begin()) {
        Serial.println("[Setup] Warning: I2S INMP441 Microphone initialization failed.");
    }

    // 6. Initialize Battery Monitor
    batteryMonitor.begin();

    // 7. Initialize SPIFFS Offline Queue
    if (!LocalStorage::begin()) {
        Serial.println("[Setup] Warning: SPIFFS initialization failed.");
    }

    // 8. Initialize WiFi
    WiFiManager::init();

    // 9. Initialize Emergency Manager
    EmergencyManager::init(&actuators, &gpsSensor, &batteryMonitor);

    // 10. Spawn FreeRTOS Tasks across Dual Cores
    // Core 0: High-priority Audio Task (Continuous I2S clap listening)
    xTaskCreatePinnedToCore(
        audioTask,
        "AudioTask",
        8192,
        NULL,
        2, // Higher priority
        &audioTaskHandle,
        0  // Pin to Core 0
    );

    // Core 1: System Supervisor Task (Sensors, GPS, WiFi, Alarms)
    xTaskCreatePinnedToCore(
        supervisorTask,
        "SupervisorTask",
        8192,
        NULL,
        1,
        &supervisorTaskHandle,
        1  // Pin to Core 1
    );

    Serial.println("[Setup] SafeRoute Saheli Wearable OS Initialized Successfully.\n");
}

void loop() {
    // Empty: Execution handled entirely by FreeRTOS tasks on Core 0 and Core 1
    vTaskDelay(pdMS_TO_TICKS(1000));
}
