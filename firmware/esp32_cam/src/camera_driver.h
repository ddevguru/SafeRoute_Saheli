#ifndef SAHELI_CAMERA_DRIVER_H
#define SAHELI_CAMERA_DRIVER_H

#include <Arduino.h>
#include "esp_camera.h"
#include "camera_config.h"

class CameraDriver {
public:
    static bool initCamera(framesize_t frameSize = FRAMESIZE_VGA, int jpegQuality = 12);
    static camera_fb_t* captureFrame();
    static void releaseFrame(camera_fb_t* fb);
    static void setFlashLED(bool state);
    static void pulseFlash(int durationMs = 150);
    static bool isInitialized();
    static bool hasPSRAM();
    static size_t getFreePSRAM();

private:
    static bool _initialized;
    static camera_config_t _config;
};

#endif // SAHELI_CAMERA_DRIVER_H
