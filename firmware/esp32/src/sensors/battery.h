#ifndef SAHELI_BATTERY_H
#define SAHELI_BATTERY_H

#include <Arduino.h>

class BatteryMonitor {
public:
    BatteryMonitor(uint8_t adcPin, float dividerRatio = 2.0f);
    void begin();
    float readVoltage();
    int readPercentage();
    bool isLowBattery() const;
    bool isCriticalBattery() const;

private:
    uint8_t _adcPin;
    float _dividerRatio;
    float _lastVoltage;
};

#endif // SAHELI_BATTERY_H
