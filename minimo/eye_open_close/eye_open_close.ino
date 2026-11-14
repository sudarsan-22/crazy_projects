// Robot eyes for ESP32-C3 Super Mini + 0.96" SSD1306 OLED (128x64, I2C)
//
// - Eyes blink (close/open) at random intervals, sometimes double-blink
// - Eyes glance around randomly
// - 5 expressions: Normal, Happy, Sad, Angry, Surprised (smoothly morphed)
// - Auto-cycles expressions; or send over Serial (115200):
//     1..5 = pick expression, a = auto cycle, b = blink now
//
// Wiring (typical): OLED VCC->3V3, GND->GND, SDA->GPIO8, SCL->GPIO9.
// Other pin pairs are auto-detected at boot, so most wirings just work.

#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>

U8G2 *oled = nullptr;

// ---------------------------------------------------------------- expressions
enum Mood { NORMAL, HAPPY, SAD, ANGRY, SURPRISED, MOOD_COUNT };
const char *MOOD_NAMES[MOOD_COUNT] = {"Normal", "Happy", "Sad", "Angry", "Surprised"};

struct EyeShape {
  float w, h, r;   // eye width, height, corner radius
  float lidIn;     // top lid depth at inner corner (fraction of height)
  float lidOut;    // top lid depth at outer corner
  float lidBot;    // bottom "smile" lid depth (happy ^ ^ eyes)
  float offY;      // vertical offset of the eyes
};

const EyeShape SHAPES[MOOD_COUNT] = {
  //  w   h   r   lidIn lidOut lidBot offY
  {  36, 36,  8,  0.00, 0.00,  0.00,   0 },  // Normal
  {  36, 34, 10,  0.00, 0.00,  0.50,  -2 },  // Happy
  {  34, 32,  8,  0.05, 0.50,  0.00,   4 },  // Sad   (outer corners droop)
  {  38, 30,  6,  0.55, 0.05,  0.00,   2 },  // Angry (inner corners down)
  {  30, 44, 14,  0.00, 0.00,  0.00,  -2 },  // Surprised (tall, round)
};

const int      EYE_GAP     = 14;     // pixels between the two eyes
const uint32_t MOOD_MS     = 4000;   // time per expression in auto mode

Mood     mood       = NORMAL;
bool     autoMode   = true;
uint32_t moodSince  = 0;
EyeShape cur        = SHAPES[NORMAL];  // current (animated) shape

// ---------------------------------------------------------------- blink
bool     blinking   = false;
uint32_t blinkStart = 0;
uint32_t nextBlink  = 0;

float blinkOpenness(uint32_t now) {
  const uint32_t CLOSE = 80, HOLD = 50, OPEN = 120;
  if (!blinking) {
    if ((int32_t)(now - nextBlink) < 0) return 1.0f;
    blinking = true;
    blinkStart = now;
  }
  uint32_t t = now - blinkStart;
  if (t < CLOSE) return 1.0f - (float)t / CLOSE;
  if (t < CLOSE + HOLD) return 0.0f;
  if (t < CLOSE + HOLD + OPEN) return (float)(t - CLOSE - HOLD) / OPEN;

  blinking = false;
  // 20% chance of a quick double blink
  nextBlink = now + (random(100) < 20 ? 150 : random(1800, 4500));
  return 1.0f;
}

// ---------------------------------------------------------------- look around
float    lookX = 0, lookY = 0, lookTX = 0, lookTY = 0;
uint32_t nextLook = 0;

void updateLook(uint32_t now) {
  if ((int32_t)(now - nextLook) >= 0) {
    if (random(100) < 40) { lookTX = 0; lookTY = 0; }
    else { lookTX = random(-10, 11); lookTY = random(-5, 6); }
    nextLook = now + random(1200, 4000);
  }
  lookX += (lookTX - lookX) * 0.25f;
  lookY += (lookTY - lookY) * 0.25f;
}

// ---------------------------------------------------------------- drawing
void drawEye(float cx, float cy, const EyeShape &s, float open, bool isLeft) {
  int w = (int)(s.w + 0.5f);
  int h = (int)(s.h * open + 0.5f);
  int x = (int)(cx - w / 2.0f);

  oled->setDrawColor(1);
  if (h <= 3) {                       // fully closed: a thin line
    oled->drawBox(x, (int)cy - 1, w, 2);
    return;
  }
  int y = (int)(cy - h / 2.0f);
  int r = min((int)s.r, min(w, h) / 2 - 1);
  if (r < 0) r = 0;
  oled->drawRBox(x, y, w, h, r);

  // Erase parts of the eye with black lids to form the expression
  oled->setDrawColor(0);

  float inH = h * s.lidIn, outH = h * s.lidOut;
  if (inH > 0.5f || outH > 0.5f) {
    int xl = x - 2, xr = x + w + 2, yt = y - 2;
    int yIn = y + (int)inH, yOut = y + (int)outH;
    int yL = isLeft ? yOut : yIn;     // left eye: outer corner is on the left
    int yR = isLeft ? yIn : yOut;
    oled->drawTriangle(xl, yt, xr, yt, xr, yR);
    oled->drawTriangle(xl, yt, xr, yR, xl, yL);
  }

  if (s.lidBot > 0.01f) {             // curved bottom lid -> happy "^ ^"
    int ry  = (int)(h * s.lidBot + h * 0.2f);
    int cyE = y + h + (int)(h * 0.2f);
    oled->drawFilledEllipse((int)cx, cyE, (int)(w * 0.8f), ry);
  }
  oled->setDrawColor(1);
}

void render(uint32_t now, float open) {
  float bounce = (mood == HAPPY) ? sinf(now / 180.0f) * 2.0f : 0.0f;
  float cy = 32 + cur.offY + lookY + bounce;
  float leftCx  = 64 - EYE_GAP / 2.0f - cur.w / 2.0f + lookX;
  float rightCx = 64 + EYE_GAP / 2.0f + cur.w / 2.0f + lookX;

  oled->clearBuffer();
  drawEye(leftCx,  cy, cur, open, true);
  drawEye(rightCx, cy, cur, open, false);
  oled->sendBuffer();
}

// ---------------------------------------------------------------- control
void setMood(Mood m, uint32_t now) {
  mood = m;
  moodSince = now;
  nextBlink = now;                    // blink while changing expression
  Serial.printf("Expression: %s\n", MOOD_NAMES[m]);
}

void handleSerial(uint32_t now) {
  while (Serial.available()) {
    char c = Serial.read();
    if (c >= '1' && c < '1' + MOOD_COUNT) { autoMode = false; setMood((Mood)(c - '1'), now); }
    else if (c == 'a') { autoMode = true; Serial.println("Auto mode"); }
    else if (c == 'b') { nextBlink = now; }
  }
}

static inline void approach(float &v, float target) { v += (target - v) * 0.2f; }

// ---------------------------------------------------------------- I2C detect
bool probeOled(int sda, int scl, uint8_t &addr) {
  if (!Wire.begin(sda, scl, 100000)) return false;
  bool found = false;
  for (uint8_t a : {0x3C, 0x3D}) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) { addr = a; found = true; break; }
  }
  Wire.end();
  return found;
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.printf("Reset reason: %d\n", (int)esp_reset_reason());
  randomSeed(esp_random());

  // Candidate SDA/SCL pairs (skips USB pins 18/19 and flash pins 11-17)
  const int pairs[][2] = {
    {8, 9}, {9, 8}, {5, 6}, {6, 5}, {4, 5}, {5, 4}, {6, 7}, {7, 6},
    {3, 4}, {4, 3}, {2, 3}, {3, 2}, {0, 1}, {1, 0}, {20, 21}, {21, 20},
  };
  int sda = 8, scl = 9;
  uint8_t addr = 0x3C;
  bool found = false;
  for (auto &p : pairs) {
    if (probeOled(p[0], p[1], addr)) { sda = p[0]; scl = p[1]; found = true; break; }
  }
  if (found) Serial.printf("OLED found at 0x%02X on SDA=%d SCL=%d\n", addr, sda, scl);
  else       Serial.println("OLED not detected! Trying SDA=8 SCL=9 anyway. Check wiring.");

  oled = new U8G2_SSD1306_128X64_NONAME_F_HW_I2C(U8G2_R0, U8X8_PIN_NONE, scl, sda);
  oled->setI2CAddress(addr << 1);
  oled->setBusClock(400000);
  oled->begin();

  uint32_t now = millis();
  nextBlink = now + 1000;
  nextLook  = now + 1500;
  setMood(NORMAL, now);
  Serial.println("Send 1-5 to pick expression, a = auto, b = blink");
}

void loop() {
  uint32_t now = millis();
  handleSerial(now);

  if (autoMode && now - moodSince > MOOD_MS) setMood((Mood)((mood + 1) % MOOD_COUNT), now);

  const EyeShape &t = SHAPES[mood];
  approach(cur.w, t.w);       approach(cur.h, t.h);       approach(cur.r, t.r);
  approach(cur.lidIn, t.lidIn); approach(cur.lidOut, t.lidOut);
  approach(cur.lidBot, t.lidBot); approach(cur.offY, t.offY);

  updateLook(now);
  render(now, blinkOpenness(now));
}
