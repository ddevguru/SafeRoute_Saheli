#include "camera_driver.h"

bool CameraDriver::_initialized = false;
camera_config_t CameraDriver::_config;

bool CameraDriver::initCamera(framesize_t frameSize, int jpegQuality) {
    pinMode(PIN_FLASH_LED, OUTPUT);
    digitalWrite(PIN_FLASH_LED, LOW);

    pinMode(PIN_STATUS_LED, OUTPUT);
    digitalWrite(PIN_STATUS_LED, HIGH); // Active LOW -> OFF

    _config.ledc_channel = LEDC_CHANNEL_0;
    _config.ledc_timer = LEDC_TIMER_0;
    _config.pin_d0 = Y2_GPIO_NUM;
    _config.pin_d1 = Y3_GPIO_NUM;
    _config.pin_d2 = Y4_GPIO_NUM;
    _config.pin_d3 = Y5_GPIO_NUM;
    _config.pin_d4 = Y6_GPIO_NUM;
    _config.pin_d5 = Y7_GPIO_NUM;
    _config.pin_d6 = Y8_GPIO_NUM;
    _config.pin_d7 = Y9_GPIO_NUM;
    _config.pin_xclk = XCLK_GPIO_NUM;
    _config.pin_pclk = PCLK_GPIO_NUM;
    _config.pin_vsync = VSYNC_GPIO_NUM;
    _config.pin_href = HREF_GPIO_NUM;
    _config.pin_sscb_sda = SIOD_GPIO_NUM;
    _config.pin_sscb_scl = SIOC_GPIO_NUM;
    _config.pin_pwdn = PWDN_GPIO_NUM;
    _config.pin_reset = RESET_GPIO_NUM;
    _config.xclk_freq_hz = 20000000;
    _config.pixel_format = PIXFORMAT_JPEG;

    // Check PSRAM availability
    if (psramFound()) {
        Serial.println("[CameraDriver] PSRAM detected! Enabling high resolution & double buffering.");
        _config.frame_size = frameSize;
        _config.jpeg_quality = jpegQuality;
        _config.fb_count = 2;
        _config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
        Serial.println("[CameraDriver] Warning: No PSRAM detected. Restricting to SVGA and single buffer.");
        _config.frame_size = FRAMESIZE_SVGA;
        _config.jpeg_quality = 16;
        _config.fb_count = 1;
        _config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    }

    esp_err_t err = esp_camera_init(&_config);
    if (err != ESP_OK) {
        Serial.printf("[CameraDriver] Camera init failed with error 0x%x\n", err);
        _initialized = false;
        return false;
    }

    sensor_t* s = esp_camera_sensor_get();
    if (s != nullptr) {
        // AI-Thinker OV2640 initial tuning
        s->set_brightness(s, 1);     // -2 to 2
        s->set_contrast(s, 1);       // -2 to 2
        s->set_saturation(s, 0);     // -2 to 2
        s->set_special_effect(s, 0); // 0 = No Effect
        s->set_whitebal(s, 1);       // 0 = Disable, 1 = Enable
        s->set_awb_gain(s, 1);       // 0 = Disable, 1 = Enable
        s->set_wb_mode(s, 0);        // 0 = Auto
    }

    _initialized = true;
    Serial.println("[CameraDriver] OV2640 Camera initialized successfully.");
    return true;
}

camera_fb_t* CameraDriver::captureFrame() {
    if (!_initialized) {
        Serial.println("[CameraDriver] Cannot capture: Camera not initialized.");
        return nullptr;
    }
    return esp_camera_fb_get();
}

void CameraDriver::releaseFrame(camera_fb_t* fb) {
    if (fb != nullptr) {
        esp_camera_fb_return(fb);
    }
}

void CameraDriver::setFlashLED(bool state) {
    digitalWrite(PIN_FLASH_LED, state ? HIGH : LOW);
}

void CameraDriver::pulseFlash(int durationMs) {
    setFlashLED(true);
    delay(durationMs);
    setFlashLED(false);
}

bool CameraDriver::isInitialized() {
    return _initialized;
}

bool CameraDriver::hasPSRAM() {
    return psramFound();
}

size_t CameraDriver::getFreePSRAM() {
    if (psramFound()) {
        return ESP.getFreePsram();
    }
    return 0;
}
