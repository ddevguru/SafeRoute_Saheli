#ifndef SAHELI_CAM_CONFIG_H
#define SAHELI_CAM_CONFIG_H

#include <Arduino.h>

// ============================================================================
// 1. NETWORK & BACKEND CLOUD CREDENTIALS
// ============================================================================
#define WIFI_SSID             "SaheliSecureWiFi"
#define WIFI_PASSWORD         "StaySafe@2026"
#define BACKEND_BASE_URL      "http://192.168.1.100:5000/api"
#define DEVICE_ID             "SAHELI-CAM-001"
#define DEVICE_SECRET         "cam_esp32_shared_secret_2026"
#define FIRMWARE_VERSION      "1.0.0"

// Authenticated Stream Port & Authorization Key
#define STREAM_SERVER_PORT    81
#define STREAM_AUTH_KEY       "SaheliStreamKey2026"

// ============================================================================
// 2. AI-THINKER ESP32-CAM PIN MAPPINGS
// ============================================================================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Actuator & Status LEDs
#define PIN_FLASH_LED      4     // High-intensity white flashlight LED
#define PIN_STATUS_LED    33     // Active LOW small onboard red LED

// ============================================================================
// 3. CAPTURE & TIMING CONFIGURATION
// ============================================================================
#define HEARTBEAT_INTERVAL_MS 30000 // 30-sec health report to cloud
#define BURST_FRAME_COUNT     5     // 5 rapid snapshot frames on emergency trigger
#define BURST_FRAME_DELAY_MS  300   // 300ms interval between burst frames

#endif // SAHELI_CAM_CONFIG_H
