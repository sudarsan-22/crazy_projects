#include <Arduino.h>

const int testPins[] = {0, 1, 2, 3, 4, 5, 6, 7, 10, 20, 21};
const int nPins = sizeof(testPins) / sizeof(testPins[0]);
int prevVal[nPins];

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== Touch Pin Live Sniffer ===");
  Serial.println("Touch your TTP223 sensor repeatedly now!");

  for (int i = 0; i < nPins; i++) {
    pinMode(testPins[i], INPUT);
    prevVal[i] = digitalRead(testPins[i]);
  }
}

void loop() {
  for (int i = 0; i < nPins; i++) {
    int val = digitalRead(testPins[i]);
    if (val != prevVal[i]) {
      Serial.printf(">>> PIN CHANGED! GPIO %d is now %d <<<\n", testPins[i], val);
      prevVal[i] = val;
    }
  }
  delay(10);
}
