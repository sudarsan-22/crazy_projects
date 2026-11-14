/*
 ==============================================================================
   MINIMO GIRLY EDITION - Interactive Cyber Companion Desk Pet
   Target: DFRobot Beetle ESP32-C3 v2.0.0
   Display: 0.96" I2C OLED (SSD1306, 128x64, SDA=8, SCL=9)
   Sensor: TTP223 on GPIO 2 ONLY (Integrated inside the top bow)
   Battery: 300-500mAh Li-ion (Onboard TP4057 USB-C Charging)
   
   Girly Features & Charm:
   - Big expressive eyes with fluttery eyelashes & 4-point twinkling star pupils
   - Glowing heart blush cheeks
   - Instant zero-latency capacitive touch detection via the bow (GPIO 2 interrupt)
   - 1 Tap:   Instant Happy Smile & Sparkle Gaze ("SPARKLE & SHINE! ✨")
   - 2 Taps:  Instant Beating Heart Eyes & Rosy Blush ("LOVE YOU BESTIE! 💕")
   - 3 Taps:  Instant Strawberry Treat NomNom 🍓 ("YUM! STRAWBERRY 🍓")
   - Hold:    Instant Cozy Snuggle Mode ("SO COZY & CUTE! 🌸")
   - Inactive: Auto-sleep after 45s with animated floating pink Zzz snoring bubbles
   - Wake:    Touching the bow immediately wakes the pet with zero lag!
 ==============================================================================
*/

#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>

// ------------------------------------------------------------- Pin Definitions
#define TOUCH_PIN             2       // GPIO 2 ONLY (TTP223 Bow Sensor)
#define I2C_SDA_PIN           8       // Beetle ESP32-C3 default SDA
#define I2C_SCL_PIN           9       // Beetle ESP32-C3 default SCL

// ------------------------------------------------------------- 1.3" OLED Driver
// Most 1.3" I2C OLED modules (128x64) use the SH1106 controller.
// Set to 1 for SH1106, or 0 if your 1.3" module uses SSD1306.
#define USE_SH1106_1_3_INCH   1

#if USE_SH1106_1_3_INCH
// 1.3" SH1106 128x64 Hardware I2C (Standard 1.3" Blue/White OLED)
U8G2_SH1106_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE, I2C_SCL_PIN, I2C_SDA_PIN);
#else
// 1.3" SSD1306 128x64 Hardware I2C
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE, I2C_SCL_PIN, I2C_SDA_PIN);
#endif

// ---------------------------------------------------------------- Pet Moods
enum GirlyMood {
  GIRLY_NORMAL = 0,
  GIRLY_HAPPY,
  GIRLY_LOVE,
  GIRLY_SWEET_SNACK,
  GIRLY_SURPRISED,
  GIRLY_WINK,
  GIRLY_SLEEPY,
  GIRLY_MOOD_COUNT
};

GirlyMood curMood        = GIRLY_NORMAL;
bool      isAsleep       = false;
uint32_t  lastTouchTime  = 0;
const uint32_t AUTO_SLEEP_MS = 45000; // Sleep after 45s of no touch

// Mood auto-cycle timer
uint32_t moodTimer      = 0;
uint32_t moodDuration   = 6000;
uint32_t lastIdleRender = 0;

// --------------------------------------- Hardware Interrupt State Machine
volatile int       tapSequence       = 0;
volatile uint32_t  lastTapTime       = 0;
volatile uint32_t  touchDownTime     = 0;
volatile bool      isTouching        = false;
volatile bool      needInstantRender = false;
volatile GirlyMood pendingMood       = GIRLY_NORMAL;
const char*        pendingSpeech     = nullptr;
bool               longHoldTriggered = false;

// ----------------------------------------------------------- Speech Quotes
const char *GIRLY_QUOTES[] = {
  "PAT MY BOW! \xE2\x9C\xA8",
  "YOU ARE SO PRETTY! \xF0\x9F\x92\x95",
  "SPARKLE TIME! \xE2\x9C\xA8",
  "BESTIE FOR LIFE \xF0\x9F\x92\x95",
  "SWEET DREAMS \xF0\x9F\x8C\xB8",
  "STRAWBERRY TREAT \xF0\x9F\x8D\x93",
  "COZY DESK VIBES \xE2\x99\xA1",
  "YOU GOT THIS GIRL! \xF0\x9F\x92\xAA",
  "TWINKLE TWINKLE \xE2\x9C\xA8",
  "CUTE & PROUD \xF0\x9F\x8E\x80"
};
const int TOTAL_QUOTES = sizeof(GIRLY_QUOTES) / sizeof(GIRLY_QUOTES[0]);

const char *activeQuote       = nullptr;
bool        showSpeechBubble  = false;
uint32_t    speechStartMs     = 0;
uint32_t    nextSpeechMs      = 8000;
const uint32_t SPEECH_DURATION = 2400;

// ------------------------------------------------- Animated Gaze & Blinking
float gazeX = 0, gazeY = 0;
float targetGazeX = 0, targetGazeY = 0;
uint32_t nextGazeChange = 0;

bool     blinking    = false;
uint32_t blinkStart  = 0;
uint32_t nextBlink   = 0;
float    blinkFactor = 1.0f; // 1.0 = open, 0.0 = closed

// -------------------------------------------------------------- Helper Math
static inline void approach(float &val, float target, float rate) {
  val += (target - val) * rate;
}

void drawCenteredStr(int y, const uint8_t *font, const char *str) {
  oled.setFont(font);
  int w = oled.getStrWidth(str);
  int x = (128 - w) / 2;
  if (x < 0) x = 0;
  oled.drawStr(x, y, str);
}

// Draw a cartoon heart
void drawHeart(int cx, int cy, int size) {
  int r = size / 2;
  oled.drawDisc(cx - r/2, cy - r/3, r/2);
  oled.drawDisc(cx + r/2, cy - r/3, r/2);
  oled.drawTriangle(cx - size/2 - 1, cy - r/4,
                    cx + size/2 + 1, cy - r/4,
                    cx, cy + size/2 + 2);
}

// ---------------------------------------------------- Cute Girly Muzzle
void drawGirlyMuzzle(int cx, int cy, bool happy) {
  // Tiny cute nose dot
  oled.drawDisc(cx, cy + 2, 2);

  if (happy) {
    // Joyful curved smile (w)
    oled.drawArc(cx - 3, cy + 5, 3, 0, 180);
    oled.drawArc(cx + 3, cy + 5, 3, 0, 180);
  } else {
    // Gentle soft smile
    oled.drawArc(cx - 3, cy + 4, 3, 0, 180);
    oled.drawArc(cx + 3, cy + 4, 3, 0, 180);
  }
}

// Heart / Sparkle Blush Cheeks
void drawGirlyBlush(int leftX, int rightX, int y) {
  // Left cheek blush lines
  oled.drawLine(leftX - 2, y, leftX, y + 4);
  oled.drawLine(leftX + 2, y, leftX + 4, y + 4);
  oled.drawLine(leftX + 6, y, leftX + 8, y + 4);

  // Right cheek blush lines
  oled.drawLine(rightX - 8, y, rightX - 6, y + 4);
  oled.drawLine(rightX - 4, y, rightX - 2, y + 4);
  oled.drawLine(rightX, y, rightX + 2, y + 4);
}

// Eyelashes drawn above eye
void drawEyelashes(int cx, int cy, int eyeW, int eyeH, int side) {
  int topY = cy - eyeH/2 - 1;
  int tipX = cx + (side * (eyeW/2 + 2));
  
  // Upper flutter lash 1
  oled.drawLine(cx + (side * 4), topY + 1, tipX, topY - 3);
  // Upper flutter lash 2
  oled.drawLine(cx + (side * 8), topY + 3, tipX + (side * 2), topY);
}

// ----------------------------------------------------------- Speech Bubble
void drawSpeechBubble(const char *text) {
  oled.setFont(u8g2_font_5x8_tr);
  int strW = oled.getStrWidth(text);
  int boxW = strW + 8;
  int boxH = 11;
  int boxX = 64 - boxW / 2;
  int boxY = 1;

  if (boxX < 2) boxX = 2;
  if (boxX + boxW > 126) boxX = 126 - boxW;

  oled.setDrawColor(0);
  oled.drawBox(boxX - 1, boxY - 1, boxW + 2, boxH + 2);
  oled.setDrawColor(1);
  oled.drawRFrame(boxX, boxY, boxW, boxH, 3);

  // Tail pointing to head
  oled.drawTriangle(61, boxY + boxH - 1, 67, boxY + boxH - 1, 64, boxY + boxH + 3);
  oled.setDrawColor(0);
  oled.drawLine(62, boxY + boxH - 1, 66, boxY + boxH - 1);

  oled.setDrawColor(1);
  oled.drawStr(boxX + 4, boxY + 8, text);
}

// ------------------------------------------------------------- Blink Engine
void updateBlinking(uint32_t now) {
  if (isAsleep || curMood == GIRLY_SLEEPY) {
    blinkFactor = 0.0f;
    return;
  }
  if (curMood == GIRLY_HAPPY || curMood == GIRLY_LOVE) {
    blinkFactor = 1.0f;
    return;
  }

  const uint32_t CLOSE_TIME = 60;
  const uint32_t HOLD_TIME  = 30;
  const uint32_t OPEN_TIME  = 90;

  if (!blinking) {
    if ((int32_t)(now - nextBlink) >= 0) {
      blinking = true;
      blinkStart = now;
    } else {
      blinkFactor = 1.0f;
      return;
    }
  }

  uint32_t elapsed = now - blinkStart;
  if (elapsed < CLOSE_TIME) {
    blinkFactor = 1.0f - ((float)elapsed / CLOSE_TIME);
  } else if (elapsed < CLOSE_TIME + HOLD_TIME) {
    blinkFactor = 0.0f;
  } else if (elapsed < CLOSE_TIME + HOLD_TIME + OPEN_TIME) {
    blinkFactor = (float)(elapsed - CLOSE_TIME - HOLD_TIME) / OPEN_TIME;
  } else {
    blinking = false;
    blinkFactor = 1.0f;
    nextBlink = now + (random(100) < 25 ? 150 : random(2000, 5000));
  }
}

// --------------------------------------------------------------- Gaze Engine
void updateGaze(uint32_t now) {
  if (isAsleep || curMood == GIRLY_SLEEPY || curMood == GIRLY_HAPPY || curMood == GIRLY_LOVE) {
    targetGazeX = 0;
    targetGazeY = 0;
  } else if ((int32_t)(now - nextGazeChange) >= 0) {
    targetGazeX = (random(100) < 40) ? 0 : random(-8, 9);
    targetGazeY = (random(100) < 40) ? 0 : random(-4, 5);
    nextGazeChange = now + random(1400, 3200);
  }

  approach(gazeX, targetGazeX, 0.30f);
  approach(gazeY, targetGazeY, 0.30f);
}

// --------------------------------------------------------- Expression Renderers

// 1. NORMAL GIRLY (Fluttery eyelashes with starry twinkle)
void renderNormal(uint32_t now) {
  int eyeW = 24;
  int eyeH = (int)(28 * blinkFactor);
  int leftCx  = 42 + (int)gazeX;
  int rightCx = 86 + (int)gazeX;
  int cy      = 28 + (int)gazeY;

  if (eyeH > 4) {
    // Eye outer glow/frame
    oled.drawRBox(leftCx - eyeW/2, cy - eyeH/2, eyeW, eyeH, 8);
    oled.drawRBox(rightCx - eyeW/2, cy - eyeH/2, eyeW, eyeH, 8);

    // Dark iris
    oled.setDrawColor(0);
    oled.drawRBox(leftCx - eyeW/2 + 2, cy - eyeH/2 + 2, eyeW - 4, eyeH - 4, 6);
    oled.drawRBox(rightCx - eyeW/2 + 2, cy - eyeH/2 + 2, eyeW - 4, eyeH - 4, 6);

    // Twinkling Star Pupils
    oled.setDrawColor(1);
    int pOffX = (int)(gazeX * 0.4f);
    int pOffY = (int)(gazeY * 0.4f);

    // Left 4-point star highlight
    int starLx = leftCx - 3 + pOffX;
    int starLy = cy - 4 + pOffY;
    oled.drawDisc(starLx, starLy, 3);
    oled.drawLine(starLx - 5, starLy, starLx + 5, starLy);
    oled.drawLine(starLx, starLy - 5, starLx, starLy + 5);

    // Right 4-point star highlight
    int starRx = rightCx - 3 + pOffX;
    int starRy = cy - 4 + pOffY;
    oled.drawDisc(starRx, starRy, 3);
    oled.drawLine(starRx - 5, starRy, starRx + 5, starRy);
    oled.drawLine(starRx, starRy - 5, starRx, starRy + 5);

    // Eyelashes
    drawEyelashes(leftCx, cy, eyeW, eyeH, -1);
    drawEyelashes(rightCx, cy, eyeW, eyeH, 1);
  } else {
    // Closed happy curve slit
    oled.drawLine(leftCx - eyeW/2, cy, leftCx + eyeW/2, cy);
    oled.drawLine(rightCx - eyeW/2, cy, rightCx + eyeW/2, cy);
  }

  drawGirlyMuzzle(64, 40, false);
  drawGirlyBlush(leftCx - 8, rightCx + 8, 44);
}

// 2. HAPPY (Joyful curved eyes ^ ^ with blushing smile)
void renderHappy(uint32_t now) {
  int cy = 26;
  // Bouncing happy motion
  int bounce = (millis() / 140) % 2 == 0 ? 0 : 2;
  cy -= bounce;

  // Left & right smiling crescent arcs ( ^ ^ )
  for (int t = 0; t < 3; t++) {
    oled.drawCircle(42, cy + 12 - t, 12, U8G2_DRAW_UPPER_RIGHT | U8G2_DRAW_UPPER_LEFT);
    oled.drawCircle(86, cy + 12 - t, 12, U8G2_DRAW_UPPER_RIGHT | U8G2_DRAW_UPPER_LEFT);
  }

  // Eyelashes on smiling curves
  oled.drawLine(28, cy + 2, 24, cy - 1);
  oled.drawLine(32, cy, 30, cy - 4);
  oled.drawLine(100, cy + 2, 104, cy - 1);
  oled.drawLine(96, cy, 98, cy - 4);

  drawGirlyMuzzle(64, 40, true);
  drawGirlyBlush(30, 98, 42);
}

// 3. LOVE MODE (Pulsing Beating Heart Eyes ♥ ♥)
void renderLove(uint32_t now) {
  // Beating pulse effect
  float phase = (millis() % 700) / 700.0f;
  int heartSz = (phase < 0.25f) ? 18 : ((phase < 0.5f) ? 20 : 16);

  drawHeart(42, 26, heartSz);
  drawHeart(86, 26, heartSz);

  // Flutter lashes
  oled.drawLine(26, 20, 22, 17);
  oled.drawLine(102, 20, 106, 17);

  drawGirlyMuzzle(64, 42, true);
  drawGirlyBlush(28, 100, 44);
}

// 4. SWEET STRAWBERRY SNACK (Nom-nom 🍓)
void renderSweetSnack(uint32_t now) {
  int cy = 26;
  // Chewing animation
  bool chew = (millis() / 200) % 2 == 0;

  oled.drawDisc(42, cy, 7);
  oled.drawDisc(86, cy, 7);
  oled.setDrawColor(0);
  oled.drawDisc(44, cy - 2, 2);
  oled.drawDisc(88, cy - 2, 2);
  oled.setDrawColor(1);

  // Eyelashes
  oled.drawLine(34, cy - 5, 30, cy - 8);
  oled.drawLine(94, cy - 5, 98, cy - 8);

  // Strawberry Icon floating on screen
  drawHeart(64, chew ? 40 : 42, 12);
  // Strawberry green leaf crown
  oled.drawTriangle(61, 35, 67, 35, 64, 32);

  drawGirlyBlush(32, 96, 42);
}

// 5. SWEET WINK (Left eye wink, right eye sparkle)
void renderWink(uint32_t now) {
  int cy = 28;

  // Left Eye: Playful wink arc
  for (int t = 0; t < 3; t++) {
    oled.drawCircle(42, cy + 8 - t, 10, U8G2_DRAW_UPPER_RIGHT | U8G2_DRAW_UPPER_LEFT);
  }
  oled.drawLine(28, cy + 2, 24, cy - 1);
  oled.drawLine(32, cy, 30, cy - 4);

  // Right Eye: Big open sparkling star eye
  oled.drawRBox(74, cy - 14, 24, 28, 8);
  oled.setDrawColor(0);
  oled.drawRBox(76, cy - 12, 20, 24, 6);
  oled.setDrawColor(1);
  oled.drawDisc(84, cy - 4, 4);

  drawGirlyMuzzle(64, 40, true);
  drawGirlyBlush(30, 98, 44);
}

// 6. SLEEPY Zzz (Cozy sleeping mode)
void renderSleepy(uint32_t now) {
  int cy = 34;

  // Closed gentle sleeping arcs
  oled.drawArc(42, cy, 8, 180, 360);
  oled.drawArc(86, cy, 8, 180, 360);

  // Floating animated Zzz bubbles
  int zOffset = (millis() / 350) % 3;
  oled.setFont(u8g2_font_6x10_tr);
  if (zOffset >= 0) oled.drawStr(96, 24, "z");
  if (zOffset >= 1) oled.drawStr(104, 16, "Z");
  if (zOffset >= 2) oled.drawStr(114, 8, "Z");

  drawGirlyMuzzle(64, 44, false);
}

// ------------------------------------------------- Hardware Touch ISR Handler
void IRAM_ATTR onTouchISR() {
  uint32_t now = millis();
  bool pinVal = digitalRead(TOUCH_PIN);

  if (pinVal == HIGH) {
    // Touch pressed
    touchDownTime = now;
    isTouching = true;

    if (now - lastTapTime > 500) {
      tapSequence = 1;
    } else {
      tapSequence++;
    }
    lastTapTime = now;

    // Instant mood trigger
    if (tapSequence == 1) {
      pendingMood = GIRLY_HAPPY;
      pendingSpeech = "PAT PAT! \xE2\x9C\xA8";
    } else if (tapSequence == 2) {
      pendingMood = GIRLY_LOVE;
      pendingSpeech = "LOVE YOU BESTIE! \xF0\x9F\x92\x95";
    } else if (tapSequence >= 3) {
      pendingMood = GIRLY_SWEET_SNACK;
      pendingSpeech = "YUM! STRAWBERRY \xF0\x9F\x8D\x93";
    }
    needInstantRender = true;
  } else {
    isTouching = false;
  }
}

// ------------------------------------------------------------- Setup
void setup() {
  Serial.begin(115200);

  // Initialize SSD1306 OLED via Hardware I2C (800kHz Turbo Mode)
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setClock(800000);
  oled.begin();

  // Attach zero-latency hardware interrupt to Bow capacitive touch pin
  pinMode(TOUCH_PIN, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(TOUCH_PIN), onTouchISR, CHANGE);

  randomSeed(analogRead(0));
  lastTouchTime = millis();
}

// ------------------------------------------------------------- Main Loop
void loop() {
  uint32_t now = millis();

  // Handle instant interrupt renders
  if (needInstantRender) {
    needInstantRender = false;
    curMood = pendingMood;
    activeQuote = pendingSpeech;
    showSpeechBubble = true;
    speechStartMs = now;
    lastTouchTime = now;
    isAsleep = false;
  }

  // Check long press (Cozy Hug Mode)
  if (isTouching && !longHoldTriggered && (now - touchDownTime > 1200)) {
    longHoldTriggered = true;
    curMood = GIRLY_LOVE;
    activeQuote = "SO COZY! \xF0\x9F\x8C\xB8";
    showSpeechBubble = true;
    speechStartMs = now;
    lastTouchTime = now;
  }
  if (!isTouching) {
    longHoldTriggered = false;
  }

  // Auto-sleep timeout
  if (!isAsleep && (now - lastTouchTime > AUTO_SLEEP_MS)) {
    isAsleep = true;
    curMood = GIRLY_SLEEPY;
    showSpeechBubble = false;
  }

  // Speech bubble timeout
  if (showSpeechBubble && (now - speechStartMs > SPEECH_DURATION)) {
    showSpeechBubble = false;
  }

  // Periodic random idle quotes
  if (!isAsleep && !showSpeechBubble && (now > nextSpeechMs)) {
    activeQuote = GIRLY_QUOTES[random(TOTAL_QUOTES)];
    showSpeechBubble = true;
    speechStartMs = now;
    nextSpeechMs = now + random(9000, 16000);
  }

  // Update physical eye movements & blinks
  updateBlinking(now);
  updateGaze(now);

  // Render Display Frame
  oled.clearBuffer();

  switch (curMood) {
    case GIRLY_HAPPY:       renderHappy(now); break;
    case GIRLY_LOVE:        renderLove(now); break;
    case GIRLY_SWEET_SNACK: renderSweetSnack(now); break;
    case GIRLY_WINK:        renderWink(now); break;
    case GIRLY_SLEEPY:      renderSleepy(now); break;
    case GIRLY_NORMAL:
    default:                renderNormal(now); break;
  }

  if (showSpeechBubble && activeQuote) {
    drawSpeechBubble(activeQuote);
  }

  oled.sendBuffer();

  // Mood reset after interaction
  if (curMood != GIRLY_NORMAL && curMood != GIRLY_SLEEPY && (now - lastTouchTime > 4500)) {
    curMood = (random(100) < 30) ? GIRLY_WINK : GIRLY_NORMAL;
  }

  delay(20);
}
