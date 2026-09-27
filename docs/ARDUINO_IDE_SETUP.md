# SafeRoute Saheli — Arduino IDE Complete IoT Firmware Guide
## (मुख्य 2-फ़ाइल आर्डुइनो कोड एवं कनेक्शन निर्देशिका)

इस प्रोजेक्ट के सभी IoT हार्डवेयर के लिए केवल **2 सम्पूर्ण और स्वतंत्र फ़ाइलें (`.ino`)** तैयार की गई हैं, जिन्हें आप सीधे **Arduino IDE** में खोलकर फ्लैश कर सकते हैं:

1. **[saheli_esp32_main.ino](file:///c:/Safe-Route-saheli/firmware/arduino/saheli_esp32_main/saheli_esp32_main.ino)**: मुख्य स्मार्ट सेफ्टी वियरेबल डिवाइस (Main ESP32 Wearable Device).
2. **[saheli_esp32_cam.ino](file:///c:/Safe-Route-saheli/firmware/arduino/saheli_esp32_cam/saheli_esp32_cam.ino)**: एआई विजन, लाइव वीडियो स्ट्रीमिंग एवं फॉरेंसिक एविडेंस कैमरा (AI-Thinker ESP32-CAM).

---

## 1. Arduino IDE Setup (प्रारंभिक सेटअप)

### Step 1: ESP32 Board URL जोड़ें
1. Arduino IDE खोलें (`v2.0` या नवीनतम).
2. **File** -> **Preferences** में जाएं.
3. **Additional Boards Manager URLs** में यह लिंक पेस्ट करें:
   ```text
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. **Tools** -> **Board** -> **Boards Manager** खोलें और `esp32 by Espressif Systems` सर्च करके **Install** करें.

---

## 2. File 1: Main ESP32 Wearable (`saheli_esp32_main.ino`)

### हार्डवेयर पिन कनेक्शन (Circuit Diagram & Pinout)

| कॉम्पोनेंट (Component) | सेंसर पिन (Sensor Pin) | ESP32 GPIO पिन | विवरण (Notes) |
|---|---|---|---|
| **TTP223 Touch** | SIG (Signal) | **GPIO 13** | 1.5 सेकंड दबाकर रखने पर SOS ट्रिगर |
| **MPU-6050 (Motion)** | SDA | **GPIO 21** | 6-Axis I2C डेटा बस |
| | SCL | **GPIO 22** | I2C क्लॉक बस |
| | VCC / GND | 3.3V / GND | गिरावट (Fall > 2.8G) व संघर्ष (Struggle > 200°/s) |
| **NEO-6M GPS** | TX | **GPIO 16 (RX2)** | NMEA लाइव लोकेशन स्ट्रीम |
| | RX | **GPIO 17 (TX2)** | GPS कॉन्फ़िगरेशन |
| | VCC / GND | 5V (या 3.3V) / GND | सैटेलाइट फिक्स |
| **INMP441 Microphone** | SCK (BCLK) | **GPIO 26** | I2S सीरियल क्लॉक |
| | WS (LRCLK) | **GPIO 25** | I2S वर्ड सेलेक्ट |
| | SD (DIN) | **GPIO 33** | I2S डिजिटल ऑडियो डेटा |
| | L/R | GND | लेफ्ट चैनल सेलेक्ट |
| | VDD / GND | 3.3V / GND | **3-Clap (3 ताली)** पैटर्न SOS डिटेक्टर |
| **Piezo Buzzer** | (+) Signal | **GPIO 14** | ट्रांजिस्टर ड्राइवर द्वारा अलार्म सायरन |
| **Vibration Motor** | Gate Signal | **GPIO 12** | MOSFET ड्राइवर द्वारा स्पर्श प्रतिक्रिया |
| **Status LED** | Anode (+) | **GPIO 2** | ऑनबोर्ड विजुअल सिग्नल |
| **Battery ADC** | Voltage Divider Out | **GPIO 34 (ADC1)** | 100kΩ + 100kΩ डिवाइडर (LiPo 3.7V) |

### Arduino IDE बोर्ड सेटिंग्स (Main ESP32):
- **Board:** `ESP32 Dev Module` या `DOIT ESP32 DEVKIT V1`
- **Upload Speed:** `921600` (या `115200`)
- **CPU Frequency:** `240MHz (WiFi/BT)`
- **Flash Frequency:** `80MHz`
- **Port:** अपना COM पोर्ट चुनें (उदा. `COM3` / `COM4`)

### कोड में अपना WiFi सेट करें:
फ़ाइल के सबसे ऊपर अपनी WiFi जानकारी दर्ज करें:
```cpp
const char* WIFI_SSID     = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
```
*Backend URL पहले से ही Render पर सेट है:* `https://saferoute-saheli-backend.onrender.com/api`

---

## 3. File 2: ESP32-CAM AI Vision Camera (`saheli_esp32_cam.ino`)

### हार्डवेयर पिन कनेक्शन (AI-Thinker ESP32-CAM)
ESP32-CAM मॉड्यूल पर कैमरा लेंस (OV2640) और फ्लैशलाइट पहले से इन-बिल्ट होते हैं। इसे फ्लैश करने के लिए **FTDI USB-to-TTL कन्वर्टर** का उपयोग करें:

| FTDI USB-to-TTL पिन | ESP32-CAM पिन | विवरण (Notes) |
|---|---|---|
| **VCC (5V)** | **5V** | ESP32-CAM को 5V सप्लाई दें (कम से कम 1A से 2A) |
| **GND** | **GND** | कॉमन ग्राउंड |
| **TX** | **U0R (GPIO 3)** | FTDI का TX -> ESP32-CAM का RX |
| **RX** | **U0T (GPIO 1)** | FTDI का RX -> ESP32-CAM का TX |
| **GPIO 0** | **GND** | **महत्वपूर्ण:** कोड फ्लैश करते समय GPIO 0 को GND से जोड़ें! फ्लैशिंग के बाद हटा दें। |

### Arduino IDE बोर्ड सेटिंग्स (ESP32-CAM):
- **Board:** `AI Thinker ESP32-CAM`
- **CPU Frequency:** `240MHz (WiFi/BT)`
- **Flash Frequency:** `80MHz`
- **Flash Mode:** `QIO`
- **Partition Scheme:** `Huge APP (3MB No OTA/1MB SPIFFS)` ⚠️ *(यह चुनना आवश्यक है)*
- **PSRAM:** `Enabled`

### फीचर्स:
1. **लाइव MJPEG वीडियो स्ट्रीम:** किसी भी ब्राउज़र, मोबाइल ऐप या एडमिन पैनल में देखें:
   ```text
   http://<CAM_IP_ADDRESS>:81/stream
   ```
2. **क्लाउड एविडेंस अपलोड:** आपातकाल में 5 लगातार फोटो (Flash LED के साथ) खींचकर सीधे Render फॉरेंसिक वॉल्ट में अपलोड करता है:
   ```text
   https://saferoute-saheli-backend.onrender.com/api/camera/capture
   ```

---

## 4. क्लाउड आर्किटेक्चर एवं डेटाबेस इंटीग्रेशन

- **Render Live Backend:** `https://saferoute-saheli-backend.onrender.com`
- **Render PostgreSQL DB:** `postgresql://saheli_user:Rj4br2lYgQ3FkNuxtfdqVIatVD9Z4zOC@dpg-dasjh38473hc738jkep0-a/saferoute_saheli`

> [!NOTE]
> **सुरक्षा नियम (Security Best-Practice):**
> ESP32 और ESP32-CAM सीधे डेटाबेस पोर्ट को ओपन करके कनेक्ट नहीं करते (क्योंकि माइक्रोकंट्रोलर्स से डेटाबेस पासवर्ड लीक होने का जोखिम रहता है)।
> इसके बजाय, दोनों डिवाइस Render बैकएंड API (`/api/devices/events`, `/api/devices/heartbeat`, `/api/camera/capture`) के साथ सुरक्षित **HTTPS + HMAC Secret (`DEVICE_SECRET`)** द्वारा संवाद करते हैं। बैकएंड सुरक्षित रूप से डेटा को Render PostgreSQL डेटाबेस में सेव और सिंक्रनाइज़ करता है।
