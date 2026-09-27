#include "touch_sensor.h"

TouchSensor::TouchSensor(uint8_t pin, uint32_t holdTimeMs)
    : _pin(pin), _holdTimeMs(holdTimeMs), _touchStartTime(0), _isHeld(false), _hasTriggered(false) {}

void TouchSensor::begin() {
    pinMode(_pin, INPUT);
}

bool TouchSensor::update() {
    bool rawState = digitalRead(_pin) == HIGH;

    if (rawState) {
        if (!_isHeld) {
            _isHeld = true;
            _touchStartTime = millis();
        } else if (!_hasTriggered && (millis() - _touchStartTime >= _holdTimeMs)) {
            _hasTriggered = true;
            return true; // Trigger emergency event!
        }
    } else {
        _isHeld = false;
        _hasTriggered = false;
        _touchStartTime = 0;
    }

    return false;
}

bool TouchSensor::isCurrentlyTouched() const {
    return _isHeld;
}

void TouchSensor::reset() {
    _isHeld = false;
    _hasTriggered = false;
    _touchStartTime = 0;
}
