#include "battery.h"

BatteryMonitor::BatteryMonitor(uint8_t adcPin, float dividerRatio)
    : _adcPin(adcPin), _dividerRatio(dividerRatio), _lastVoltage(4.20f) {}

void BatteryMonitor::begin() {
    pinMode(_adcPin, INPUT);
    analogReadResolution(12); // 12-bit ADC (0 - 4095)
}

float BatteryMonitor::readVoltage() {
    // 10-sample moving average filter
    uint32_t rawSum = 0;
    for (int i = 0; i < 10; i++) {
        rawSum += analogRead(_adcPin);
        delay(2);
    }
    float rawAvg = rawSum / 10.0f;

    // Convert raw ADC reading to pin voltage: (rawAvg / 4095.0) * 3.3V
    float pinVoltage = (rawAvg / 4095.0f) * 3.30f;
    // Scale by voltage divider resistor ratio (e.g., 2.0 for 100k/100k)
    _lastVoltage = pinVoltage * _dividerRatio;

    return _lastVoltage;
}

int BatteryMonitor::readPercentage() {
    float voltage = readVoltage();
    // Li-Po 1S curve approximation: 3.2V (0%) to 4.2V (100%)
    if (voltage >= 4.20f) return 100;
    if (voltage <= 3.20f) return 0;

    int percent = (int)(((voltage - 3.20f) / (4.20f - 3.20f)) * 100.0f);
    return constrain(percent, 0, 100);
}

bool BatteryMonitor::isLowBattery() const {
    return _lastVoltage < 3.50f; // Approx 20%
}

bool BatteryMonitor::isCriticalBattery() const {
    return _lastVoltage < 3.35f; // Approx 10%
}
