#include "actuators.h"

Actuators::Actuators(uint8_t buzzerPin, uint8_t vibrationPin, uint8_t ledPin)
    : _buzzerPin(buzzerPin), _vibrationPin(vibrationPin), _ledPin(ledPin),
      _isAlarmActive(false), _lastToggleTime(0), _toggleState(false) {}

void Actuators::begin() {
    pinMode(_buzzerPin, OUTPUT);
    pinMode(_vibrationPin, OUTPUT);
    pinMode(_ledPin, OUTPUT);

    digitalWrite(_buzzerPin, LOW);
    digitalWrite(_vibrationPin, LOW);
    digitalWrite(_ledPin, LOW);
}

void Actuators::setAlarmState(bool active) {
    _isAlarmActive = active;
    if (!active) {
        digitalWrite(_buzzerPin, LOW);
        digitalWrite(_vibrationPin, LOW);
        digitalWrite(_ledPin, LOW);
    }
}

void Actuators::update() {
    if (!_isAlarmActive) return;

    // Siren oscillation: Toggle every 120ms for piercing emergency tone
    uint32_t now = millis();
    if (now - _lastToggleTime >= 120) {
        _lastToggleTime = now;
        _toggleState = !_toggleState;

        digitalWrite(_buzzerPin, _toggleState ? HIGH : LOW);
        digitalWrite(_vibrationPin, _toggleState ? HIGH : LOW);
        digitalWrite(_ledPin, _toggleState ? HIGH : LOW);
    }
}

void Actuators::pulseVibration(uint16_t durationMs) {
    digitalWrite(_vibrationPin, HIGH);
    delay(durationMs);
    digitalWrite(_vibrationPin, LOW);
}
