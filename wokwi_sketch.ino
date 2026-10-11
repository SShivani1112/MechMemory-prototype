#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

const int TEMP_PIN = 34;
const int VIB_PIN = 35;
const int GREEN_LED = 18;
const int RED_LED = 19;

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// Replace with your active HTTPS tunnel base URL. No trailing slash.
// Example: https://your-name.ngrok-free.app
const char* API_BASE_URL = "YOUR_NGROK_HTTPS_URL";

void setup() {
  Serial.begin(115200);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wokwi-GUEST");
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  int tempRaw = analogRead(TEMP_PIN);
  int vibRaw = analogRead(VIB_PIN);

  float temperature = 20.0 + (tempRaw / 4095.0) * 80.0;
  float vibration = (vibRaw / 4095.0) * 10.0;
  bool failure = (temperature > 70.0 || vibration > 7.0);

  digitalWrite(GREEN_LED, failure ? LOW : HIGH);
  digitalWrite(RED_LED, failure ? HIGH : LOW);

  Serial.printf("T=%.1f C, V=%.2f, Status=%s\n",
                temperature, vibration, failure ? "ANOMALY" : "NORMAL");

  if (WiFi.status() == WL_CONNECTED &&
      String(API_BASE_URL) != "YOUR_NGROK_HTTPS_URL") {
    WiFiClientSecure secureClient;
    // Prototype only: skips certificate validation for the temporary tunnel.
    // Do not use this approach for production or sensitive data.
    secureClient.setInsecure();

    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/readings";
    if (http.begin(secureClient, url)) {
      http.addHeader("Content-Type", "application/json");
      http.setTimeout(5000);

      String body = "{\"machine_id\":\"MCH-001\",\"temperature\":";
      body += String(temperature, 1);
      body += ",\"vibration\":";
      body += String(vibration, 2);
      body += "}";

      int code = http.POST(body);
      Serial.printf("POST -> HTTP %d\n", code);
      if (code > 0) Serial.println(http.getString());
      http.end();
    } else {
      Serial.println("Could not initialize HTTPS request.");
    }
  } else {
    Serial.println("API URL not configured or WiFi disconnected.");
  }

  delay(2000);
}
