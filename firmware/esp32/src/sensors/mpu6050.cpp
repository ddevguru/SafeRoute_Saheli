#include "mpu6050.h"
#include <math.h>

MPU6050Sensor::MPU6050Sensor(uint8_t sdaPin, uint8_t sclPin)
    : _sdaPin(sdaPin), _sclPin(sclPin), _initialized(false), _lastFallCheckTime(0) {}

bool MPU6050Sensor::begin() {
    Wire.begin(_sdaPin, _sclPin);
    
    // Wake up MPU-6050 (write 0 to PWR_MGMT_1 register 0x6B)
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x6B);
    Wire.write(0x00);
    uint8_t error = Wire.endTransmission();

    if (error == 0) {
        _initialized = true;
        // Set accelerometer range to +/- 8g (Register 0x1C)
        Wire.beginTransmission(MPU_ADDR);
        Wire.write(0x1C);
        Wire.write(0x10);
        Wire.endTransmission();

        // Set gyroscope range to +/- 1000 deg/s (Register 0x1B)
        Wire.beginTransmission(MPU_ADDR);
        Wire.write(0x1B);
        Wire.write(0x10);
        Wire.endTransmission();
        return true;
    }
    return false;
}

MotionData MPU6050Sensor::read() {
    MotionData data = {0};
    if (!_initialized) {
        return data;
    }

    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x3B); // Start with ACCEL_XOUT_H
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_ADDR, (uint8_t)14, (uint8_t)true);

    if (Wire.available() >= 14) {
        int16_t rawAx = (Wire.read() << 8) | Wire.read();
        int16_t rawAy = (Wire.read() << 8) | Wire.read();
        int16_t rawAz = (Wire.read() << 8) | Wire.read();
        int16_t rawTemp = (Wire.read() << 8) | Wire.read();
        (void)rawTemp;
        int16_t rawGx = (Wire.read() << 8) | Wire.read();
        int16_t rawGy = (Wire.read() << 8) | Wire.read();
        int16_t rawGz = (Wire.read() << 8) | Wire.read();

        // Convert to physical units (at +/- 8g: 4096 LSB/g; at +/- 1000 deg/s: 32.8 LSB/(deg/s))
        data.accelX = rawAx / 4096.0f;
        data.accelY = rawAy / 4096.0f;
        data.accelZ = rawAz / 4096.0f;

        data.gyroX = rawGx / 32.8f;
        data.gyroY = rawGy / 32.8f;
        data.gyroZ = rawGz / 32.8f;

        // Vector Magnitudes
        data.accelMagnitude = sqrtf(data.accelX * data.accelX + data.accelY * data.accelY + data.accelZ * data.accelZ);
        data.gyroMagnitude = sqrtf(data.gyroX * data.gyroX + data.gyroY * data.gyroY + data.gyroZ * data.gyroZ);

        // Fall detection: Impact > 2.8g accompanied by high angular rotation > 180 deg/s
        data.isFallDetected = (data.accelMagnitude > 2.8f) && (data.gyroMagnitude > 180.0f);

        // Struggle detection: Rapid repetitive movements > 1.8g and high angular velocity
        data.isStruggleDetected = (data.accelMagnitude > 2.0f) && (data.gyroMagnitude > 150.0f);
    }

    return data;
}
