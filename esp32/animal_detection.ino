/*
 * FarmFusion - Real-Time Animal Intrusion Detection System
 * Target Hardware: ESP32 Dev Module (6x IR, 2x PIR, 1x Buzzer)
 *
 * SENSOR HARDWARE PIN MAPPING:
 * ------------------------------------------------------------------
 * 1. IR Sensors (6x):
 *    - IR_1: GPIO 27 (Active-LOW: 0 = Obstacle, 1 = Detecting)
 *    - IR_2: GPIO 26 (Active-LOW: 0 = Obstacle, 1 = Detecting)
 *    - IR_3: GPIO 32 (Active-LOW: 0 = Obstacle, 1 = Detecting)
 *    - IR_4: GPIO 33 (Active-LOW: 0 = Obstacle, 1 = Detecting)
 *    - IR_5: GPIO 18 (Active-LOW: 0 = Obstacle, 1 = Detecting)
 *    - IR_6: GPIO 19 (Active-LOW: 0 = Obstacle, 1 = Detecting)
 *
 * 2. PIR Motion Sensors (2x):
 *    - PIR_1: GPIO 23 (Active-HIGH: 1 = Motion, 0 = Detecting)
 *    - PIR_2: GPIO 22 (Active-HIGH: 1 = Motion, 0 = Detecting)
 *
 * 3. Alarm Output:
 *    - Buzzer: GPIO 25 (Active-HIGH)
 * ------------------------------------------------------------------
 */

#include <HTTPClient.h>
#include <WiFi.h>


// ============================================================================
// 1. CONFIGURATION
// ============================================================================
const char *WIFI_SSID = "STORM";        // Your Wi-Fi SSID
const char *WIFI_PASSWORD = "00000000"; // Your Wi-Fi Password

// Laptop IPv4 Address on Wi-Fi network
const char *SERVER_IP = "10.45.35.226";
const int SERVER_PORT = 8000;
const char *DEVICE_ID = "NODE_01";

// ============================================================================
// 2. HARDWARE PINS & TRIGGER LEVELS
// ============================================================================
// 6x IR Sensors
#define PIN_IR_1 27
#define PIN_IR_2 26
#define PIN_IR_3 32
#define PIN_IR_4 33
#define PIN_IR_5 18
#define PIN_IR_6 19

// 2x PIR Motion Sensors
#define PIN_PIR_1 23
#define PIN_PIR_2 22

// 1x Buzzer Alarm
#define PIN_BUZZER 25

#define IR_TRIGGER_LEVEL LOW   // 0 = obstacle detected
#define PIR_TRIGGER_LEVEL HIGH // 1 = motion detected

// ============================================================================
// 3. DEBOUNCE STRUCTURE & TIMING
// ============================================================================
const int NUM_SAMPLES = 5; // 5 consecutive samples required
const unsigned long SAMPLE_INTERVAL =
    30; // Sample every 30ms (150ms debounce window)
const unsigned long HOLD_TIME = 150;    // 150ms hold duration
const unsigned long HB_INTERVAL = 1500; // 1.5s Unified Heartbeat

struct DebouncedSensor {
  const char *name;
  const char *type;
  int pin;
  int triggerLevel;
  int samples[NUM_SAMPLES];
  int sampleIndex;
  bool isDetected; // True = detected, False = clear/detecting
  unsigned long lastStateChangeTime;
};

DebouncedSensor sensors[] = {
    {"IR_1", "IR", PIN_IR_1, IR_TRIGGER_LEVEL, {0}, 0, false, 0},
    {"IR_2", "IR", PIN_IR_2, IR_TRIGGER_LEVEL, {0}, 0, false, 0},
    {"IR_3", "IR", PIN_IR_3, IR_TRIGGER_LEVEL, {0}, 0, false, 0},
    {"IR_4", "IR", PIN_IR_4, IR_TRIGGER_LEVEL, {0}, 0, false, 0},
    {"IR_5", "IR", PIN_IR_5, IR_TRIGGER_LEVEL, {0}, 0, false, 0},
    {"IR_6", "IR", PIN_IR_6, IR_TRIGGER_LEVEL, {0}, 0, false, 0},
    {"PIR_1", "PIR", PIN_PIR_1, PIR_TRIGGER_LEVEL, {0}, 0, false, 0},
    {"PIR_2", "PIR", PIN_PIR_2, PIR_TRIGGER_LEVEL, {0}, 0, false, 0}};

const int NUM_SENSORS = sizeof(sensors) / sizeof(sensors[0]);

// Timers
unsigned long lastSampleTime = 0;
unsigned long lastNodeHeartbeatTime = 0;
unsigned long lastDiagTime = 0;
const unsigned long DIAG_INTERVAL = 4000;

bool wasWifiConnected = false;

// Function prototypes
void sendDetectionEvent(const char *sensorName, const char *sensorType,
                        bool isDetected);
void sendUnifiedHeartbeat();

// ============================================================================
// SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n================================================");
  Serial.println("  FarmFusion - 6x IR + 2x PIR Firmware v11.0   ");
  Serial.println("================================================");

  // Configure 6x IR Pins (INPUT_PULLUP: Idle = HIGH, Trigger = LOW)
  pinMode(PIN_IR_1, INPUT_PULLUP);
  pinMode(PIN_IR_2, INPUT_PULLUP);
  pinMode(PIN_IR_3, INPUT_PULLUP);
  pinMode(PIN_IR_4, INPUT_PULLUP);
  pinMode(PIN_IR_5, INPUT_PULLUP);
  pinMode(PIN_IR_6, INPUT_PULLUP);

  // Configure 2x PIR Pins (INPUT_PULLDOWN: Idle = LOW, Trigger = HIGH)
  pinMode(PIN_PIR_1, INPUT_PULLDOWN);
  pinMode(PIN_PIR_2, INPUT_PULLDOWN);

  // Configure Buzzer Output
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);

  // Initialize sample buffers with initial read
  for (int i = 0; i < NUM_SENSORS; i++) {
    int initialRead = digitalRead(sensors[i].pin);
    for (int j = 0; j < NUM_SAMPLES; j++) {
      sensors[i].samples[j] = initialRead;
    }
    sensors[i].isDetected = (initialRead == sensors[i].triggerLevel);
    sensors[i].lastStateChangeTime = millis();

    Serial.print("📌 Sensor ");
    Serial.print(sensors[i].name);
    Serial.print(" (Pin ");
    Serial.print(sensors[i].pin);
    Serial.print("): ");
    Serial.println(sensors[i].isDetected ? "🔴 DETECTED" : "🟢 DETECTING");
  }

  Serial.println("------------------------------------------------");

  // Configure Wi-Fi
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("📡 Connecting to Wi-Fi SSID: ");
  Serial.println(WIFI_SSID);
}

// ============================================================================
// MAIN LOOP
// ============================================================================
void loop() {
  unsigned long currentMillis = millis();
  bool isConnected = (WiFi.status() == WL_CONNECTED);

  // Wi-Fi Connection Log
  if (isConnected && !wasWifiConnected) {
    wasWifiConnected = true;
    Serial.print("✅ Wi-Fi Connected! ESP32 IP: ");
    Serial.println(WiFi.localIP());
    sendUnifiedHeartbeat(); // Immediate first unified heartbeat
  } else if (!isConnected && wasWifiConnected) {
    wasWifiConnected = false;
    Serial.println("⚠️ Wi-Fi Disconnected. Auto-reconnecting...");
  }

  // --------------------------------------------------------------------------
  // 1. FAST SENSOR SAMPLING & DEBOUNCING (Every 30ms)
  // --------------------------------------------------------------------------
  if (currentMillis - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime = currentMillis;

    for (int i = 0; i < NUM_SENSORS; i++) {
      int rawRead = digitalRead(sensors[i].pin);

      // Store sample in circular buffer
      sensors[i].samples[sensors[i].sampleIndex] = rawRead;
      sensors[i].sampleIndex = (sensors[i].sampleIndex + 1) % NUM_SAMPLES;

      // Hysteresis check: Require ALL 5 samples to match
      bool allMatch = true;
      int firstSample = sensors[i].samples[0];
      for (int k = 1; k < NUM_SAMPLES; k++) {
        if (sensors[i].samples[k] != firstSample) {
          allMatch = false;
          break;
        }
      }

      if (allMatch) {
        bool candidateState = (firstSample == sensors[i].triggerLevel);

        // Send event ONLY when a debounced state transition occurs
        if (candidateState != sensors[i].isDetected) {
          if (currentMillis - sensors[i].lastStateChangeTime >= HOLD_TIME) {
            sensors[i].isDetected = candidateState;
            sensors[i].lastStateChangeTime = currentMillis;

            Serial.print(candidateState ? "🚨 [DETECTED] " : "🟢 [CLEARED] ");
            Serial.print(sensors[i].name);
            Serial.println(candidateState ? " -> 🔴 DETECTED"
                                          : " -> 🟢 DETECTING");

            if (isConnected) {
              sendDetectionEvent(sensors[i].name, sensors[i].type,
                                 candidateState);
            }
          }
        }
      }
    }
  }

  // --------------------------------------------------------------------------
  // 2. INSTANT LOCAL BUZZER CONTROL (Any active intrusion sounds buzzer)
  // --------------------------------------------------------------------------
  bool anyIntrusion = false;
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (sensors[i].isDetected) {
      anyIntrusion = true;
      break;
    }
  }
  digitalWrite(PIN_BUZZER, anyIntrusion ? HIGH : LOW);

  // --------------------------------------------------------------------------
  // 3. PERIODIC UNIFIED HEARTBEAT (Every 1.5 seconds)
  // --------------------------------------------------------------------------
  if (currentMillis - lastNodeHeartbeatTime >= HB_INTERVAL) {
    lastNodeHeartbeatTime = currentMillis;
    if (isConnected) {
      sendUnifiedHeartbeat();
    }
  }

  // --------------------------------------------------------------------------
  // 4. PERIODIC SERIAL DIAGNOSTICS (Every 4.0 seconds)
  // --------------------------------------------------------------------------
  if (currentMillis - lastDiagTime >= DIAG_INTERVAL) {
    lastDiagTime = currentMillis;
    Serial.print("🔍 [SENSORS] ");
    for (int i = 0; i < NUM_SENSORS; i++) {
      Serial.print(sensors[i].name);
      Serial.print(":");
      Serial.print(sensors[i].isDetected ? "🔴" : "🟢");
      Serial.print(" ");
    }
    Serial.print("| IP: ");
    Serial.println(isConnected ? WiFi.localIP().toString()
                               : String("CONNECTING..."));
  }

  delay(5);
}

// ============================================================================
// HTTP POST REAL-TIME EVENT TELEMETRY (<10ms)
// ============================================================================
void sendDetectionEvent(const char *sensorName, const char *sensorType,
                        bool isDetected) {
  WiFiClient wifiClient;
  HTTPClient http;

  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) +
               "/api/v1/animal-detection";

  if (http.begin(wifiClient, url)) {
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(400);

    String statusStr = isDetected ? "detected" : "cleared";
    String jsonPayload = "{";
    jsonPayload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    jsonPayload += "\"sensor\":\"" + String(sensorName) + "\",";
    jsonPayload += "\"sensor_type\":\"" + String(sensorType) + "\",";
    jsonPayload += "\"status\":\"" + statusStr + "\"";
    jsonPayload += "}";

    int httpCode = http.POST(jsonPayload);
    if (httpCode == 201 || httpCode == 200) {
      Serial.print("   ↳ 📡 Event POST Success: ");
      Serial.print(sensorName);
      Serial.print(" -> ");
      Serial.println(statusStr);
    }
    http.end();
  }
}

// ============================================================================
// HTTP POST UNIFIED HEARTBEAT (All 8 Sensors Refreshed)
// ============================================================================
void sendUnifiedHeartbeat() {
  WiFiClient wifiClient;
  HTTPClient http;

  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) +
               "/api/v1/animal-detection/heartbeat";

  if (http.begin(wifiClient, url)) {
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(500);

    String jsonPayload = "{";
    jsonPayload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    jsonPayload += "\"sensors\":{";
    for (int i = 0; i < NUM_SENSORS; i++) {
      jsonPayload += "\"" + String(sensors[i].name) + "\":\"";
      jsonPayload +=
          String(sensors[i].isDetected ? "detected" : "cleared") + "\"";
      if (i < NUM_SENSORS - 1)
        jsonPayload += ",";
    }
    jsonPayload += "}}";

    int httpCode = http.POST(jsonPayload);
    if (httpCode == 200) {
      Serial.println("💓 Unified Heartbeat ACK (8 Sensors)");
    }
    http.end();
  }
}
