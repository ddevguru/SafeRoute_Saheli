#ifndef SAHELI_GPS_H
#define SAHELI_GPS_H

#include <Arduino.h>
#include <TinyGPSPlus.h>

struct GPSLocation {
    double latitude;
    double longitude;
    float accuracyMeters;
    float speedKmph;
    float headingDeg;
    uint32_t satellites;
    bool hasFix;
    String timestampIso;
};

class GPSSensor {
public:
    GPSSensor(uint8_t rxPin, uint8_t txPin, uint32_t baudRate = 9600);
    void begin();
    void update(); // Must be called frequently in supervisor loop
    GPSLocation getLocation();
    bool hasValidFix() const;

private:
    uint8_t _rxPin;
    uint8_t _txPin;
    uint32_t _baudRate;
    HardwareSerial _serial;
    TinyGPSPlus _gpsParser;
};

#endif // SAHELI_GPS_H
