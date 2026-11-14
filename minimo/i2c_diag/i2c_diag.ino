#include <Arduino.h>
#include <Wire.h>

const int gpios[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21};
const int nGpios = sizeof(gpios) / sizeof(gpios[0]);

void scanPins(int sda, int scl) {
  Wire.begin(sda, scl, 100000);
  Wire.setTimeOut(15);
  for (uint8_t a = 0x38; a <= 0x3F; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.printf("\n>>> MATCH FOUND! SDA=GPIO%d, SCL=GPIO%d, Addr=0x%02X <<<\n", sda, scl, a);
    }
  }
  Wire.end();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- Scanning ALL Beetle ESP32-C3 Pin Combinations ---");

  for (int i = 0; i < nGpios; i++) {
    for (int j = 0; j < nGpios; j++) {
      if (i == j) continue;
      scanPins(gpios[i], gpios[j]);
    }
  }
  Serial.println("--- Full pin matrix scan finished ---");
}

void loop() {
  delay(2000);
}
