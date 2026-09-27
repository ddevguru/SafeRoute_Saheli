#ifndef SAHELI_MAX30102_H
#define SAHELI_MAX30102_H

#include <Arduino.h>
#include <Wire.h>

struct BiometricData {
    float heartRateBpm;
    float spO2Percentage;
    bool isFingerDetected;
    bool isPanicTachycardia;
    float stressIndex;        // 0.0 (Calm) to 1.0 (Acute Panic/Tachycardia)
    uint32_t rawRed;
    uint32_t rawIR;
};

class MAX30102Sensor {
public:
    MAX30102Sensor(uint8_t sdaPin, uint8_t sclPin);
    bool begin();
    BiometricData read();
    void setBaselineBpm(float bpm);
    float getBaselineBpm() const;

private:
    uint8_t _sdaPin;
    uint8_t _sclPin;
    bool _initialized;
    float _baselineBpm;

    // Registers
    static const uint8_t MAX30102_ADDR      = 0x57;
    static const uint8_t REG_INTR_STATUS_1  = 0x00;
    static const uint8_t REG_FIFO_WR_PTR    = 0x04;
    static const uint8_t REG_OVF_COUNTER    = 0x05;
    static const uint8_t REG_FIFO_RD_PTR    = 0x06;
    static const uint8_t REG_FIFO_DATA      = 0x07;
    static const uint8_t REG_FIFO_CONFIG    = 0x08;
    static const uint8_t REG_MODE_CONFIG    = 0x09;
    static const uint8_t REG_SPO2_CONFIG    = 0x0A;
    static const uint8_t REG_LED1_PA        = 0x0C; // Red LED
    static const uint8_t REG_LED2_PA        = 0x0D; // IR LED
    static const uint8_t REG_PART_ID        = 0xFF; // Part ID (0x15)

    // Beat detection state
    uint32_t _lastBeatTime;
    float _bpmHistory[4];
    uint8_t _bpmIndex;
    float _filteredBpm;
    float _filteredSpO2;

    void writeRegister(uint8_t reg, uint8_t value);
    uint8_t readRegister(uint8_t reg);
};

#endif // SAHELI_MAX30102_H
