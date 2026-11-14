#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  delay(1000);
  pinMode(2, INPUT_PULLDOWN);
  pinMode(3, INPUT_PULLDOWN);
  pinMode(6, INPUT_PULLDOWN);
  Serial.println("Watching with INPUT_PULLDOWN...");
}

void loop() {
  int v2 = digitalRead(2);
  int v3 = digitalRead(3);
  int v6 = digitalRead(6);
  static int last2 = -1, last3 = -1, last6 = -1;
  if (v2 != last2 || v3 != last3 || v6 != last6) {
    Serial.printf("GPIO 2: %d | GPIO 3: %d | GPIO 6: %d\n", v2, v3, v6);
    last2 = v2;
    last3 = v3;
    last6 = v6;
  }
  delay(20);
}
