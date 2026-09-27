#ifndef SAHELI_CONFIG_H
#define SAHELI_CONFIG_H

#include <Arduino.h>

// ============================================================================
// 1. NETWORK & BACKEND CONFIGURATION
// ============================================================================
#define WIFI_SSID             "SaheliSecureWiFi"
#define WIFI_PASSWORD         "StaySafe@2026"
#define BACKEND_BASE_URL      "http://192.168.1.100:5000/api"
#define DEVICE_ID             "SAHELI-WEARABLE-001"
#define DEVICE_SECRET         "wearable_esp32_hmac_shared_secret_2026"
#define FIRMWARE_VERSION      "1.0.0"

// ============================================================================
// 2. HARDWARE PIN DEFINITIONS (CONFIGURABLE — NEVER HARD-CODED IN LOGIC)
// ============================================================================

// TTP223 Capacitive Touch Emergency Sensor
#define PIN_TOUCH_SENSOR      13    // Active HIGH on touch

// MPU6050 6-Axis Accelerometer & Gyroscope (I2C)
#define PIN_I2C_SDA           21
#define PIN_I2C_SCL           22

// NEO-6M GPS Module (UART 2)
#define PIN_GPS_RX            16    // ESP32 RX2 connects to GPS TX
#define PIN_GPS_TX            17    // ESP32 TX2 connects to GPS RX
#define GPS_BAUD_RATE         9600

// INMP441 I2S Digital Omnidirectional Microphone
#define PIN_I2S_SCK           26    // Serial Clock (BCLK)
#define PIN_I2S_WS            25    // Word Select (LRCLK)
#define PIN_I2S_SD            33    // Serial Data Out (DIN)

// Battery Monitoring (ADC 1)
#define PIN_BATTERY_ADC       34    // Voltage divider (R1=100k, R2=100k -> 2:1 ratio)

// Actuators
#define PIN_BUZZER            14    // Piezo Buzzer driven via NPN transistor
#define PIN_VIBRATION_MOSFET  12    // Haptic motor driven via Logic MOSFET with flyback diode
#define PIN_STATUS_LED        2     // Onboard status LED indicator

// ============================================================================
// 3. SENSOR DETECTION THRESHOLDS & PARAMETERS
// ============================================================================

// TTP223 Touch Timing
#define TOUCH_HOLD_TRIGGER_MS 1500  // 1.5 seconds continuous touch triggers emergency
#define TOUCH_DEBOUNCE_MS     50

// Clap Detection Parameters (INMP441)
#define CLAP_AMPLITUDE_THRESH 12000 // PCM peak amplitude threshold for clap
#define CLAP_MIN_INTERVAL_MS  180   // Minimum gap between rapid claps
#define CLAP_MAX_INTERVAL_MS  700   // Maximum gap between consecutive claps
#define CLAP_PATTERN_COUNT    3     // Default: 3 rapid claps to trigger emergency
#define CLAP_COOLDOWN_MS      3000  // Cooldown after trigger

// MPU6050 Motion Anomaly Parameters
#define MPU_FALL_ACCEL_G      2.8f  // Acceleration vector magnitude threshold for fall impact
#define MPU_GYRO_RATE_DPS     200.0f// Angular velocity threshold for struggle/tumble

// MAX30102 Biometric Pulse Oximeter Parameters
#define MAX30102_I2C_ADDR     0x57  // MAX30102 factory I2C slave address
#define PANIC_BPM_THRESHOLD   130.0f// Acute tachycardia panic trigger threshold (BPM)
#define PANIC_BPM_DELTA       40.0f // Sudden BPM surge above baseline
#define MIN_VALID_SPO2        85.0f // Hypoxia detection threshold

// Battery Voltage Parameters (Li-Po 1S: 3.2V empty to 4.2V full)
#define BATTERY_MIN_VOLTAGE   3.20f
#define BATTERY_MAX_VOLTAGE   4.20f
#define BATTERY_ADC_DIVIDER   2.0f  // 100k / (100k + 100k) = 0.5 -> multiplier is 2.0
#define ADC_REF_VOLTAGE       3.30f
#define ADC_RESOLUTION        4095.0f

// ============================================================================
// 4. TIMING & INTERVALS
// ============================================================================
#define INTERVAL_NORMAL_GPS_MS      25000 // 25 seconds normal update
#define INTERVAL_EMERGENCY_GPS_MS   5000  // 5 seconds high-frequency emergency stream
#define INTERVAL_HEARTBEAT_MS       30000 // 30 seconds health heartbeat
#define EMERGENCY_ALARM_DURATION_MS 60000 // 60 seconds buzzer/vib continuous cycle

#endif // SAHELI_CONFIG_H
