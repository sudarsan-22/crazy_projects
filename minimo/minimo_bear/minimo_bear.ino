/*
 ==============================================================================
   MINIMO BEAR - Interactive Cyber Bear Desk Pet
   Target: DFRobot Beetle ESP32-C3 v2.0.0
   Display: 0.96" I2C OLED (SSD1306, 128x64, SDA=8, SCL=9)
   Sensor: TTP223 on GPIO 2 ONLY (Hardware Interrupt Driven)
   Battery: 300mAh Li-ion (Onboard TP4057 USB-C Charging)
   
   Instant Zero-Latency Touch Architecture:
   - Hardware Interrupt on GPIO 2 (IRAM_ATTR) -> Nanosecond touch detection!
   - True 800kHz High-Speed I2C for instant screen rendering
   - 1 Tap:   Instant Happy Smile & Giggle ʕ ^ ᴥ ^ ʔ ("PAT PAT! ʕ^ᴥ^ʔ")
   - 2 Taps:  Instant Beating Heart Eyes   ʕ ♥ ᴥ ♥ ʔ ("LOVE YOU! ♥")
   - 3 Taps:  Instant Honey Snack & NomNom 🍯         ("YUM! HONEY 🍯")
   - Hold:    Instant Cozy Love Mode       ʕ ♥ ᴥ ♥ ʔ ("SO COZY! ♥")
   - Inactive: Auto-sleep after 45s with animated floating Zzz snoring bubbles
   - Wake:    Touching the head immediately wakes the bear with zero lag!
 ==============================================================================
*/

#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>

// ------------------------------------------------------------- Pin Definitions
#define TOUCH_PIN             2       // GPIO 2 ONLY (TTP223 head sensor)
#define I2C_SDA_PIN           8       // Beetle ESP32-C3 default SDA
#define I2C_SCL_PIN           9       // Beetle ESP32-C3 default SCL

// 0.96" SSD1306 OLED (128x64, Hardware I2C)
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE, I2C_SCL_PIN, I2C_SDA_PIN);

// ---------------------------------------------------------------- Bear Moods
enum BearMood {
  BEAR_NORMAL = 0,
  BEAR_HAPPY,
  BEAR_LOVE,
  BEAR_HONEY,
  BEAR_SURPRISED,
  BEAR_SASSY,
  BEAR_SLEEPY,
  BEAR_MOOD_COUNT
};

const char *MOOD_NAMES[BEAR_MOOD_COUNT] = {
  "Normal", "Happy Pats", "Love & Hearts", "Honey Snack",
  "Surprised", "Sassy", "Sleepy Zzz"
};

BearMood curMood         = BEAR_NORMAL;
bool     isAsleep        = false;
uint32_t lastTouchTime   = 0;
const uint32_t AUTO_SLEEP_MS = 45000; // Sleep after 45s of no touch

// Mood auto-cycle timer (when awake and not recently petted)
uint32_t moodTimer      = 0;
uint32_t moodDuration   = 6000;
uint32_t lastIdleRender = 0;

// --------------------------------------- Hardware Interrupt State Machine
volatile int      tapSequence       = 0;
volatile uint32_t lastTapTime       = 0;
volatile uint32_t touchDownTime     = 0;
volatile bool     isTouching        = false;
volatile bool     needInstantRender = false;
volatile BearMood pendingMood       = BEAR_NORMAL;
const char*       pendingSpeech     = nullptr;
bool              longHoldTriggered = false;

// ----------------------------------------------------------- Speech Bubbles
const char *BEAR_QUOTES[] = {
  "PAT MY HEAD!",
  "MORE PETS PLEASE!",
  "GIGGLE! TICKLES",
  "SUDARSAN'S BEAR",
  "BEST BEAR BUDDY",
  "I SMELL HONEY 🍯",
  "BEAR HUG TIME!",
  "100% FLUFF & SASS",
  "CAN WE HIBERNATE?",
  "GOOD HUMAN! :3",
  "SCRATCH MY EARS",
  "Zzz.. 5 MORE MINS",
  "DON'T POKE MY NOSE"
};
const int TOTAL_QUOTES = sizeof(BEAR_QUOTES) / sizeof(BEAR_QUOTES[0]);

const char *activeQuote       = nullptr;
bool        showSpeechBubble  = false;
uint32_t    speechStartMs     = 0;
uint32_t    nextSpeechMs      = 8000;
const uint32_t SPEECH_DURATION = 2200;

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

// ------------------------------------------------------------- Bear Muzzle
void drawBearMuzzle(int cx, int cy, bool openMouth, bool licking) {
  // Triangular nose
  oled.drawTriangle(cx - 5, cy, cx + 5, cy, cx, cy + 4);

  // Vertical cleft line
  oled.drawLine(cx, cy + 4, cx, cy + 7);

  if (openMouth) {
    // Happy open mouth (D)
    oled.drawCircle(cx, cy + 8, 5);
    oled.setDrawColor(0);
    oled.drawBox(cx - 6, cy + 3, 12, 5);
    oled.setDrawColor(1);
    oled.drawLine(cx - 5, cy + 8, cx + 5, cy + 8);
  } else if (licking) {
    // Licking tongue sticking out to the side
    oled.drawArc(cx - 4, cy + 8, 3, 0, 180);
    oled.drawArc(cx + 4, cy + 8, 3, 0, 180);
    oled.drawRBox(cx + 1, cy + 7, 7, 6, 3);
    oled.setDrawColor(0);
    oled.drawLine(cx + 4, cy + 7, cx + 4, cy + 10);
    oled.setDrawColor(1);
  } else {
    // Classic cute bear muzzle arcs ( ᴥ )
    oled.drawArc(cx - 4, cy + 8, 3, 0, 180);
    oled.drawArc(cx + 4, cy + 8, 3, 0, 180);
  }
}

// Blushing cheeks // //
void drawBlush(int leftX, int rightX, int y) {
  oled.drawLine(leftX, y, leftX + 3, y + 4);
  oled.drawLine(leftX + 4, y, leftX + 7, y + 4);
  oled.drawLine(rightX, y, rightX + 3, y + 4);
  oled.drawLine(rightX + 4, y, rightX + 7, y + 4);
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

  // Tail
  oled.drawTriangle(61, boxY + boxH - 1, 67, boxY + boxH - 1, 64, boxY + boxH + 3);
  oled.setDrawColor(0);
  oled.drawLine(62, boxY + boxH - 1, 66, boxY + boxH - 1);

  oled.setDrawColor(1);
  oled.drawStr(boxX + 4, boxY + 8, text);
}

// ------------------------------------------------------------- Blink Engine
void updateBlinking(uint32_t now) {
  if (isAsleep || curMood == BEAR_SLEEPY) {
    blinkFactor = 0.0f;
    return;
  }
  if (curMood == BEAR_HAPPY || curMood == BEAR_LOVE) {
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
  if (isAsleep || curMood == BEAR_SLEEPY || curMood == BEAR_HAPPY || curMood == BEAR_LOVE) {
    targetGazeX = 0;
    targetGazeY = 0;
  } else if ((int32_t)(now - nextGazeChange) >= 0) {
    if (curMood == BEAR_SASSY) {
      targetGazeX = (random(100) < 50) ? 12.0f : -12.0f;
      targetGazeY = 0.0f;
      nextGazeChange = now + random(2000, 3500);
    } else {
      targetGazeX = (random(100) < 40) ? 0 : random(-9, 10);
      targetGazeY = (random(100) < 40) ? 0 : random(-5, 6);
      nextGazeChange = now + random(1200, 3000);
    }
  }

  approach(gazeX, targetGazeX, 0.30f);
  approach(gazeY, targetGazeY, 0.30f);
}

// --------------------------------------------------------- Expression Renderers

// 1. NORMAL BEAR (Cute wandering gaze)
void renderNormal(uint32_t now) {
  int eyeW = 24;
  int eyeH = (int)(28 * blinkFactor);
  int leftCx  = 44 + (int)gazeX;
  int rightCx = 84 + (int)gazeX;
  int cy      = 26 + (int)gazeY;

  if (eyeH <= 2) {
    oled.drawBox(leftCx - eyeW/2, cy, eyeW, 2);
    oled.drawBox(rightCx - eyeW/2, cy, eyeW, 2);
  } else {
    int y = cy - eyeH / 2;
    oled.drawRBox(leftCx - eyeW/2, y, eyeW, eyeH, 6);
    oled.drawRBox(rightCx - eyeW/2, y, eyeW, eyeH, 6);

    // Highlights
    if (eyeH > 12) {
      oled.setDrawColor(0);
      oled.drawDisc(leftCx + 4, y + 7, 3);
      oled.drawDisc(rightCx + 4, y + 7, 3);
      oled.drawPixel(leftCx + 7, y + 11);
      oled.drawPixel(rightCx + 7, y + 11);
      oled.setDrawColor(1);
    }
  }

  drawBearMuzzle(64, 46, false, false);
}

// 2. HAPPY PATS (1 TAP: Smiling curved eyes ʕ ^ ᴥ ^ ʔ)
void renderHappy(uint32_t now) {
  float bounce = sinf(now * 0.012f) * 1.5f;
  int cy = 25 + (int)bounce;

  // Closed happy upside-down curved eyes: ^  ^
  oled.drawArc(44, cy, 11, 200, 340);
  oled.drawArc(44, cy - 1, 11, 200, 340);
  oled.drawArc(84, cy, 11, 200, 340);
  oled.drawArc(84, cy - 1, 11, 200, 340);

  drawBlush(24, 96, 36);
  drawBearMuzzle(64, 46, true, false);
}

// 3. LOVE BEAR (2 TAPS / HOLD: Beating cartoon hearts ʕ ♥ ᴥ ♥ ʔ)
void renderLove(uint32_t now) {
  float beat = sinf(now * 0.011f);
  int heartSize = 20 + (int)(beat * 4.0f);

  drawHeart(44, 25, heartSize);
  drawHeart(84, 25, heartSize);

  drawBlush(22, 98, 38);
  drawBearMuzzle(64, 47, true, false);
}

// 4. HONEY SNACK (3 TAPS: Licking lips 🍯)
void renderHoney(uint32_t now) {
  int eyeW = 22, eyeH = 24;
  int leftX = 44 - eyeW/2, rightX = 84 - eyeW/2, y = 14;

  oled.drawRBox(leftX, y, eyeW, eyeH, 5);
  oled.drawRBox(rightX, y, eyeW, eyeH, 5);

  oled.setDrawColor(0);
  oled.drawDisc(44, y + 15, 3);
  oled.drawDisc(84, y + 15, 3);
  oled.setDrawColor(1);

  drawBearMuzzle(64, 46, false, true);

  // Honey pot icon
  oled.drawRFrame(108, 38, 16, 20, 3);
  oled.drawLine(106, 38, 126, 38);
  oled.setFont(u8g2_font_5x8_tr);
  oled.drawStr(113, 52, "H");
}

// 5. SURPRISED BEAR ʕ o ᴥ o ʔ
void renderSurprised(uint32_t now) {
  oled.drawDisc(44, 24, 13);
  oled.drawDisc(84, 24, 13);

  oled.setDrawColor(0);
  oled.drawDisc(44 + 4, 20, 4);
  oled.drawDisc(84 + 4, 20, 4);
  oled.setDrawColor(1);

  oled.drawTriangle(60, 44, 68, 44, 64, 48);
  oled.drawLine(64, 48, 64, 51);
  oled.drawCircle(64, 56, 4);
}

// 6. SASSY BEAR ʕ ¬ ᴥ ¬ ʔ
void renderSassy(uint32_t now) {
  int eyeW = 28, eyeH = 14;
  int y = 20;

  oled.drawRBox(44 - eyeW/2, y, eyeW, eyeH, 3);
  oled.drawRBox(84 - eyeW/2, y, eyeW, eyeH, 3);

  oled.setDrawColor(0);
  int offset = (gazeX >= 0) ? (eyeW - 8) : 2;
  oled.drawBox(44 - eyeW/2 + offset, y + 2, 6, eyeH - 4);
  oled.drawBox(84 - eyeW/2 + offset, y + 2, 6, eyeH - 4);
  oled.setDrawColor(1);

  oled.drawTriangle(61, 46, 67, 46, 64, 49);
  oled.drawLine(64, 49, 64, 53);
  oled.drawLine(58, 56, 70, 53);
}

// 7. SLEEPY BEAR (Floating animated Zzz)
void renderSleepy(uint32_t now) {
  int cy = 28;
  oled.drawArc(44, cy, 10, 30, 150);
  oled.drawArc(44, cy - 1, 10, 30, 150);
  oled.drawArc(84, cy, 10, 30, 150);
  oled.drawArc(84, cy - 1, 10, 30, 150);

  float breath = sinf(now * 0.003f);
  int r = 2 + (int)(breath * 1.5f);
  if (r < 1) r = 1;

  oled.drawTriangle(61, 46, 67, 46, 64, 49);
  oled.drawLine(64, 49, 64, 53);
  oled.drawCircle(64, 55, r);

  // Floating comic 'Z' letters
  oled.setFont(u8g2_font_6x10_tr);
  for (int i = 0; i < 3; i++) {
    uint32_t zTime = now + (i * 900);
    int progress = (zTime / 24) % 55;
    int zX = 86 + (i * 10) + (int)(sinf(progress * 0.15f) * 4);
    int zY = 52 - progress;
    if (zY > 4 && zY < 58) {
      if (i == 0) oled.setFont(u8g2_font_5x8_tr);
      else if (i == 1) oled.setFont(u8g2_font_6x10_tr);
      else oled.setFont(u8g2_font_7x14_tr);
      oled.drawStr(zX, zY, "Z");
    }
  }
}

// ------------------------------------------------------------- Master Render
void render(uint32_t now) {
  oled.clearBuffer();

  if (isAsleep) {
    renderSleepy(now);
  } else {
    switch (curMood) {
      case BEAR_NORMAL:    renderNormal(now); break;
      case BEAR_HAPPY:     renderHappy(now); break;
      case BEAR_LOVE:      renderLove(now); break;
      case BEAR_HONEY:     renderHoney(now); break;
      case BEAR_SURPRISED: renderSurprised(now); break;
      case BEAR_SASSY:     renderSassy(now); break;
      case BEAR_SLEEPY:    renderSleepy(now); break;
      default:             renderNormal(now); break;
    }

    // Display speech bubble if active
    if (showSpeechBubble && activeQuote) {
      if (now - speechStartMs < SPEECH_DURATION) {
        drawSpeechBubble(activeQuote);
      } else {
        showSpeechBubble = false;
        activeQuote = nullptr;
        nextSpeechMs = now + random(6000, 14000);
      }
    }
  }

  oled.sendBuffer();
  lastIdleRender = now; // Guarantee idle timer is reset, preventing double-rendering
}

// --------------------------------------------------------------- Mood Switch
void setMood(BearMood m, uint32_t now) {
  curMood = m;
  moodTimer = now;
  blinking = false;
  blinkFactor = 1.0f;
}

void say(const char *text, uint32_t now) {
  activeQuote = text;
  showSpeechBubble = true;
  speechStartMs = now;
}

void triggerSpeechBubble(uint32_t now) {
  int idx = random(TOTAL_QUOTES);
  say(BEAR_QUOTES[idx], now);
}

// -------------------------------------------------- Hardware Interrupt (ISR)
// Triggers instantly at the silicon level in nanoseconds!
void IRAM_ATTR touchISR() {
  uint32_t now = millis();
  int pinVal = digitalRead(TOUCH_PIN);

  if (pinVal == HIGH) {
    // 20ms fast debounce allows lightning-quick consecutive taps!
    if (now - lastTapTime > 20) {
      if (now - lastTapTime < 450) {
        tapSequence++;
      } else {
        tapSequence = 1;
      }
      lastTapTime   = now;
      touchDownTime = now;
      isTouching    = true;

      // Assign instant mood based on tap sequence
      if (isAsleep) {
        pendingMood   = BEAR_HAPPY;
        pendingSpeech = "HELLO SUDARSAN!";
        isAsleep      = false;
      } else if (tapSequence == 1) {
        pendingMood   = BEAR_HAPPY;
        pendingSpeech = "PAT PAT! ^_^";
      } else if (tapSequence == 2) {
        pendingMood   = BEAR_LOVE;
        pendingSpeech = "LOVE YOU! <3";
      } else if (tapSequence >= 3) {
        pendingMood   = BEAR_HONEY;
        pendingSpeech = "YUM! HONEY!";
        tapSequence   = 0;
      }

      needInstantRender = true;
    }
  } else {
    isTouching = false;
  }
}

// -------------------------------------------------------- Cute Intro Sequence
void playIntroAnimation() {
  Serial.println("[Minimo Bear] Playing cute intro for Sudarsan...");

  // Phase 1: Waking up
  for (int h = 2; h <= 26; h += 2) {
    oled.clearBuffer();
    int y = 26 - h / 2;
    oled.drawRBox(44 - 12, y, 24, h, 6);
    oled.drawRBox(84 - 12, y, 24, h, 6);
    if (h > 12) {
      oled.setDrawColor(0);
      oled.drawDisc(44 + 4, y + 6, 3);
      oled.drawDisc(84 + 4, y + 6, 3);
      oled.setDrawColor(1);
    }
    drawBearMuzzle(64, 46, false, false);
    oled.sendBuffer();
    delay(25);
  }
  delay(300);

  // Phase 2: "Hello, I'm Minimo Bear!"
  uint32_t introStart = millis();
  while (millis() - introStart < 2400) {
    uint32_t t = millis() - introStart;
    float bounce = sinf(t * 0.008f) * 2.0f;

    oled.clearBuffer();
    oled.drawRFrame(3, 3, 122, 58, 6);
    oled.drawRFrame(5, 5, 118, 54, 4);

    drawCenteredStr(18 + (int)bounce, u8g2_font_6x10_tr, "HELLO! I'M");
    drawCenteredStr(34 + (int)bounce, u8g2_font_7x14B_tr, "MINIMO BEAR");
    drawCenteredStr(49 + (int)bounce, u8g2_font_6x10_tr, "ʕ *  ᴥ  * ʔ");

    oled.sendBuffer();
    delay(20);
  }

  // Phase 3: "Sudarsan's Cute Desk Pet!"
  introStart = millis();
  while (millis() - introStart < 2600) {
    uint32_t t = millis() - introStart;
    float beat = fabsf(sinf(t * 0.007f));
    int heartSize = 12 + (int)(beat * 5.0f);

    oled.clearBuffer();
    oled.drawRFrame(3, 3, 122, 58, 6);
    oled.drawRFrame(5, 5, 118, 54, 4);

    drawCenteredStr(18, u8g2_font_6x10_tr, "SUDARSAN'S");
    drawCenteredStr(33, u8g2_font_7x14B_tr, "DESK BUDDY!");

    drawHeart(34, 47, heartSize);
    drawHeart(94, 47, heartSize);
    drawCenteredStr(49, u8g2_font_6x10_tr, "<3  <3");

    oled.sendBuffer();
    delay(20);
  }

  // Phase 4: "PAT MY HEAD!" prompt
  oled.clearBuffer();
  oled.drawRFrame(4, 4, 120, 56, 5);
  drawCenteredStr(22, u8g2_font_7x14B_tr, "PAT MY HEAD!");
  drawCenteredStr(38, u8g2_font_6x10_tr, "ʕ ^  ᴥ  ^ ʔ");
  drawCenteredStr(52, u8g2_font_5x8_tr, "^ TOUCH TOP SENSOR ^");
  oled.sendBuffer();
  delay(1200);
}

// --------------------------------------------------------------------- Setup
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("\n======================================");
  Serial.println("     MINIMO BEAR - Cyber Desk Pet     ");
  Serial.println("======================================");

  // Configure GPIO 2 with internal pull-down resistor
  pinMode(TOUCH_PIN, INPUT_PULLDOWN);

  randomSeed(esp_random());

  // Initialize 0.96" SSD1306 OLED at True 800kHz Fast I2C
  oled.setBusClock(800000);
  oled.begin();
  Wire.setClock(800000);
  oled.setBusClock(800000);

  // Play boot welcome sequence
  playIntroAnimation();

  uint32_t now = millis();
  lastTouchTime  = now;
  moodTimer      = now;
  nextBlink      = now + 1000;
  nextGazeChange = now + 1400;
  nextSpeechMs   = now + 5000;

  setMood(BEAR_NORMAL, now);
  render(now);

  // Attach Hardware Interrupt on GPIO 2 for ANY state change
  attachInterrupt(digitalPinToInterrupt(TOUCH_PIN), touchISR, CHANGE);

  Serial.println("[Minimo Bear] Hardware Interrupt active on GPIO 2! Zero delay!");
}

// ---------------------------------------------------------------------- Loop
void loop() {
  uint32_t now = millis();

  // 1. Process Instant Touch Interrupt (Zero latency response!)
  if (needInstantRender) {
    needInstantRender = false;
    noInterrupts();
    BearMood m = pendingMood;
    const char* s = pendingSpeech;
    interrupts();

    lastTouchTime = now;
    longHoldTriggered = false;
    setMood(m, now);
    moodDuration = 4500;
    if (s) say(s, now);

    // Instant zero-delay screen update!
    render(now);
    return; // Done! Skip idle rendering!
  }

  // 2. Continuous stroke / long hold (> 1100ms)
  if (isTouching && !longHoldTriggered && (now - touchDownTime > 1100)) {
    longHoldTriggered = true;
    lastTouchTime = now;
    setMood(BEAR_LOVE, now);
    moodDuration = 5500;
    say("SO COZY! <3", now);
    render(now);
    return;
  }

  // 3. Auto-sleep check (if not touched for 45s)
  if (!isAsleep && (now - lastTouchTime > AUTO_SLEEP_MS)) {
    isAsleep = true;
    setMood(BEAR_SLEEPY, now);
    render(now);
    return;
  }

  // 4. Idle mood auto-switch (only when awake and returning to normal)
  if (!isAsleep && (now - moodTimer > moodDuration)) {
    if (curMood == BEAR_HAPPY || curMood == BEAR_LOVE || curMood == BEAR_HONEY) {
      setMood(BEAR_NORMAL, now);
      moodDuration = random(5000, 8000);
    } else {
      BearMood idleMoods[] = {BEAR_NORMAL, BEAR_SASSY, BEAR_SURPRISED};
      BearMood next = idleMoods[random(3)];
      setMood(next, now);
      moodDuration = random(4000, 7000);
    }
    render(now);
    return;
  }

  // 5. Random comic speech bubbles when idle
  if (!isAsleep && !showSpeechBubble && (int32_t)(now - nextSpeechMs) >= 0) {
    triggerSpeechBubble(now);
    render(now);
    return;
  }

  // 6. Idle Animation Engine (~15 FPS, interval = 65ms)
  // At 800kHz I2C, 1 full frame = 18.2ms.
  // When idle and static in BEAR_NORMAL, we DO NOT send redundant frames,
  // leaving the I2C bus 100% FREE so finger taps trigger INSTANTLY!
  if (now - lastIdleRender >= 65) {
    updateBlinking(now);
    updateGaze(now);

    bool needsRedraw = false;
    if (curMood != BEAR_NORMAL) {
      // Animated moods: Happy bounce, Love heartbeat, Honey tongue, Sleepy Zzz
      needsRedraw = true;
    } else if (blinking || fabsf(gazeX - targetGazeX) > 0.1f || fabsf(gazeY - targetGazeY) > 0.1f) {
      // Normal mood active movement: eyes blinking or pupils shifting
      needsRedraw = true;
    } else if (showSpeechBubble) {
      // Active speech bubble timer
      needsRedraw = true;
    }

    if (needsRedraw) {
      render(now);
    } else {
      lastIdleRender = now;
    }
  }

  delayMicroseconds(500);
}
