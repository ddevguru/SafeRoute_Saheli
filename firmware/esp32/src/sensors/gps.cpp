#include "gps.h"

GPSSensor::GPSSensor(uint8_t rxPin, uint8_t txPin, uint32_t baudRate)
    : _rxPin(rxPin), _txPin(txPin), _baudRate(baudRate), _serial(2) {}

void GPSSensor::begin() {
    _serial.begin(_baudRate, SERIAL_8N1, _rxPin, _txPin);
}

void GPSSensor::update() {
    while (_serial.available() > 0) {
        char c = _serial.read();
        _gpsParser.encode(c);
    }
}

GPSLocation GPSSensor::getLocation() {
    GPSLocation loc = {0};

    if (_gpsParser.location.isValid()) {
        loc.latitude = _gpsParser.location.lat();
        loc.longitude = _gpsParser.location.lng();
        loc.hasFix = true;
        loc.accuracyMeters = _gpsParser.hdop.isValid() ? (_gpsParser.hdop.hdop() * 4.0f) : 5.0f;
        loc.speedKmph = _gpsParser.speed.isValid() ? _gpsParser.speed.kmph() : 0.0f;
        loc.headingDeg = _gpsParser.course.isValid() ? _gpsParser.course.deg() : 0.0f;
        loc.satellites = _gpsParser.satellites.isValid() ? _gpsParser.satellites.value() : 0;
    } else {
        // Fallback default coordinates if satellite lock is pending indoors
        loc.latitude = 28.6139;
        loc.longitude = 77.2090;
        loc.hasFix = false;
        loc.accuracyMeters = 20.0f;
    }

    return loc;
}

bool GPSSensor::hasValidFix() const {
    return _gpsParser.location.isValid();
}
