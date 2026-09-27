#ifndef SAHELI_MPU6050_H
#define SAHELI_MPU6050_H

#include <Arduino.h>
#include <Wire.h>

struct MotionData {
    float accelX;
    float accelY;
    float accelZ;
    float gyroX;
    float gyroY;
    float gyroZ;
    float accelMagnitude;
    float gyroMagnitude;
    bool isFallDetected;
    bool isStruggleDetected;
};

class MPU6050Sensor {
public:
    MPU6050Sensor(uint8_t sdaPin, uint8_t sclPin);
    bool begin();
    MotionData read();

private:
    uint8_t _sdaPin;
    uint8_t _sclPin;
    static const uint8_t MPU_ADDR = 0x68;
    bool _initialized;
    uint32_t _lastFallCheckTime;
};

#endif // SAHELI_MPU6050_H
