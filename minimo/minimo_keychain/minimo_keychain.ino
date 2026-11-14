/*
 ==============================================================================
   MINIMO KEYCHAIN - Funny Cyber Pet Companion
   Target: ESP32-C3 SuperMini + 1.3" I2C OLED (SH1106 / SSD1306, 128x64)
   
   Features:
   - 8 Funny Animated Personalities & Expressions:
     1. NORMAL: Cute wandering gaze, natural blinking with highlights
     2. JUDGING (Side-Eye): Suspicious flat glance judging your life choices
     3. DERP: Goofy misaligned eyes with tongue sticking out (:P)
     4. DIZZY: Spinning spiral eyes & wavy wobble mouth
     5. HEART_EYES: Beating cartoon hearts in love
     6. SASSY_POUT: Cute angry baby pout with furrowed brows
     7. SLEEPY: Drifting off with floating, animated comic "Zzz"
     8. SNEEZE: Sudden scrunch "> <", screen earthquake & "ACHOO!" splash
   - Random Comic Speech Bubbles with hilarious one-liners!
   - Auto I2C Pin Detection (tests GPIO {8,9}, {5,6}, {4,5}, etc.)
   - Button support on GPIO 2 (optional tap to react / change mood)
   - Serial Monitor control at 115200 baud (type 1-8, 's', 'b', 'a')
   - Power-saving: Wi-Fi & Bluetooth radio disabled to maximize battery life
 ==============================================================================
*/

#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>

// ------------------------------------------------------------- Configuration
// Set to 1 for 1.3" OLED (SH1106), or 0 for 0.96" OLED (SSD1306)
#define USE_SH1106_1_3_INCH   1

// Optional push button pin to poke Minimo (active LOW with internal pull-up)
#define BTN_PIN               2

// ---------------------------------------------------------------- Display Init
U8G2 *oled = nullptr;

// ---------------------------------------------------------------- Mood States
enum Mood {
  MOOD_NORMAL = 0,
  MOOD_SIDE_EYE,
  MOOD_DERP,
  MOOD_DIZZY,
  MOOD_HEARTS,
  MOOD_POUT,
  MOOD_SLEEPY,
  MOOD_SNEEZE,
  MOOD_COUNT
};

const char *MOOD_NAMES[MOOD_COUNT] = {
  "Normal", "Side-Eye (Judging)", "Derp (:P)", "Dizzy",
  "Heart Eyes", "Sassy Pout", "Sleepy Zzz", "Achoo! Sneeze"
};

Mood     curMood     = MOOD_NORMAL;
bool     autoCycle   = true;
uint32_t moodTimer   = 0;
uint32_t moodDuration = 5000; // Time in ms before switching mood in auto mode

// ----------------------------------------------------------- Speech Bubbles
const char *FUNNY_QUOTES[] = {
  "HELLO SUDARSAN!",
  "SUDARSAN'S BUDDY",
  "BEST BUDS 4EVER <3",
  "WHY U LOOKIN?",
  "NEED COFFEE :(",
  "DON'T DROP ME!",
  "SUDARSAN IS COOL!",
  "100% SASS",
  "FEED ME ELECTRONS",
  "BEEP BOOP BUDDY",
  "NOT SHORT: COMPACT",
  "I SEE NO KEYS",
  "404: CARE NOT FOUND",
  "PET MY SCREEN!",
  "Zzz.. 5 MORE MINS",
  "WATCHIN YOU -_-"
};
const int TOTAL_QUOTES = sizeof(FUNNY_QUOTES) / sizeof(FUNNY_QUOTES[0]);

bool     showSpeechBubble = false;
int      currentQuoteIdx  = 0;
uint32_t speechStartMs    = 0;
uint32_t nextSpeechMs     = 9000;
const uint32_t SPEECH_DURATION = 2600; // Display bubble for 2.6 seconds

// ------------------------------------------------- Animated Gaze & Blinking
float gazeX = 0, gazeY = 0;
float targetGazeX = 0, targetGazeY = 0;
uint32_t nextGazeChange = 0;

bool     blinking   = false;
uint32_t blinkStart = 0;
uint32_t nextBlink  = 0;
float    blinkFactor = 1.0f; // 1.0 = fully open, 0.0 = fully closed

// Sneeze specific state
uint32_t sneezeStart = 0;
int      sneezeStage = 0; // 0=anticipation, 1=shake & explosion, 2=sniffle

// -------------------------------------------------------------- Helper Math
static inline void approach(float &val, float target, float rate) {
  val += (target - val) * rate;
}

// ------------------------------------------------------------- Blink Engine
void updateBlinking(uint32_t now) {
  if (curMood == MOOD_SLEEPY || curMood == MOOD_SNEEZE) {
    blinkFactor = 1.0f;
    return;
  }

  const uint32_t CLOSE_TIME = 70;
  const uint32_t HOLD_TIME  = 40;
  const uint32_t OPEN_TIME  = 110;

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
    // 25% chance of rapid double-blink
    if (random(100) < 25) {
      nextBlink = now + 120;
    } else {
      nextBlink = now + random(1800, 5000);
    }
  }
}

// --------------------------------------------------------------- Gaze Engine
void updateGaze(uint32_t now) {
  if (curMood == MOOD_SLEEPY || curMood == MOOD_SNEEZE) {
    targetGazeX = 0;
    targetGazeY = 0;
  } else if ((int32_t)(now - nextGazeChange) >= 0) {
    if (curMood == MOOD_SIDE_EYE) {
      // Look sharply sideways
      targetGazeX = (random(100) < 50) ? 14.0f : -14.0f;
      targetGazeY = 0.0f;
      nextGazeChange = now + random(2000, 4000);
    } else {
      if (random(100) < 35) {
        targetGazeX = 0;
        targetGazeY = 0;
      } else {
        targetGazeX = random(-11, 12);
        targetGazeY = random(-6, 7);
      }
      nextGazeChange = now + random(1000, 3200);
    }
  }

  approach(gazeX, targetGazeX, 0.28f);
  approach(gazeY, targetGazeY, 0.28f);
}

// ------------------------------------------------------------- Drawing Shapes
// Draw a cartoon heart
void drawHeart(int cx, int cy, int size) {
  int r = size / 2;
  oled->drawDisc(cx - r/2, cy - r/3, r/2);
  oled->drawDisc(cx + r/2, cy - r/3, r/2);
  oled->drawTriangle(cx - size/2 - 1, cy - r/4,
                     cx + size/2 + 1, cy - r/4,
                     cx, cy + size/2 + 2);
}

// Draw a comic speech bubble
void drawSpeechBubble(const char *text) {
  oled->setFont(u8g2_font_5x8_tr);
  int strW = oled->getStrWidth(text);
  int boxW = strW + 8;
  int boxH = 12;
  int boxX = 64 - boxW / 2;
  int boxY = 1;

  if (boxX < 2) boxX = 2;
  if (boxX + boxW > 126) boxX = 126 - boxW;

  // White bubble with rounded border
  oled->setDrawColor(0);
  oled->drawBox(boxX - 1, boxY - 1, boxW + 2, boxH + 2);
  oled->setDrawColor(1);
  oled->drawRFrame(boxX, boxY, boxW, boxH, 3);

  // Little triangular tail pointing down to face
  oled->drawTriangle(61, boxY + boxH - 1, 67, boxY + boxH - 1, 64, boxY + boxH + 3);

  // Clear inner tail for speech
  oled->setDrawColor(0);
  oled->drawLine(62, boxY + boxH - 1, 66, boxY + boxH - 1);

  // Text inside
  oled->setDrawColor(1);
  oled->drawStr(boxX + 4, boxY + 9, text);
}

// --------------------------------------------------------- Expression Renderers

// 1. NORMAL / CURIOUS
void renderNormal(uint32_t now) {
  int eyeW = 28;
  int eyeH = (int)(32 * blinkFactor);
  int cornerR = 7;
  int leftX  = 64 - 14 - eyeW + (int)gazeX;
  int rightX = 64 + 14 + (int)gazeX;
  int cy     = 31 + (int)gazeY;

  if (eyeH <= 2) {
    // Blinking flat line
    oled->drawBox(leftX, cy - 1, eyeW, 2);
    oled->drawBox(rightX, cy - 1, eyeW, 2);
    return;
  }

  int y = cy - eyeH / 2;
  oled->drawRBox(leftX, y, eyeW, eyeH, cornerR);
  oled->drawRBox(rightX, y, eyeW, eyeH, cornerR);

  // Cute white reflections inside eyes
  if (eyeH > 14) {
    oled->setDrawColor(0);
    oled->drawDisc(leftX + eyeW - 8, y + 8, 3);
    oled->drawDisc(rightX + eyeW - 8, y + 8, 3);
    oled->drawPixel(leftX + eyeW - 5, y + 13);
    oled->drawPixel(rightX + eyeW - 5, y + 13);
    oled->setDrawColor(1);
  }

  // Tiny friendly mouth
  oled->drawArc(64 + (int)(gazeX * 0.4f), 55, 4, 180, 360);
}

// 2. SIDE-EYE (JUDGING YOU)
void renderSideEye(uint32_t now) {
  int eyeW = 32;
  int eyeH = (int)(18 * blinkFactor);
  int cy = 32;
  int leftX  = 64 - 16 - eyeW;
  int rightX = 64 + 16;

  if (eyeH <= 2) {
    oled->drawBox(leftX, cy, eyeW, 2);
    oled->drawBox(rightX, cy, eyeW, 2);
  } else {
    int y = cy - eyeH / 2;
    // Slanted/narrow eyelids
    oled->drawRBox(leftX, y, eyeW, eyeH, 4);
    oled->drawRBox(rightX, y, eyeW, eyeH, 4);

    // Dark pupils looking sharply to one side
    oled->setDrawColor(0);
    int pupilOffset = (gazeX >= 0) ? (eyeW - 10) : 3;
    oled->drawBox(leftX + pupilOffset, y + 2, 7, eyeH - 4);
    oled->drawBox(rightX + pupilOffset, y + 2, 7, eyeH - 4);
    oled->setDrawColor(1);
  }

  // Flat judgmental mouth line
  oled->drawLine(57, 54, 71, 54);
}

// 3. DERP FACE (:P with goofy misaligned eyes & tongue)
void renderDerp(uint32_t now) {
  // Left eye huge, right eye tiny!
  int leftW = 32, leftH = 34;
  int rightW = 18, rightH = 20;

  int leftX = 64 - 10 - leftW;
  int leftY = 24 - leftH / 2;
  int rightX = 64 + 12;
  int rightY = 32 - rightH / 2;

  // Big left eye
  oled->drawRBox(leftX, leftY, leftW, leftH, 9);
  // Pupil top-left
  oled->setDrawColor(0);
  oled->drawDisc(leftX + 9, leftY + 11, 4);

  // Small right eye
  oled->setDrawColor(1);
  oled->drawRBox(rightX, rightY, rightW, rightH, 6);
  // Pupil bottom-right
  oled->setDrawColor(0);
  oled->drawDisc(rightX + rightW - 6, rightY + rightH - 6, 2);
  oled->setDrawColor(1);

  // Silly mouth with sticking out tongue
  oled->drawLine(54, 50, 74, 50); // Mouth line
  // Tongue
  int tongueW = 10, tongueH = 8;
  oled->drawRBox(64 - tongueW/2, 50, tongueW, tongueH, 4);
  oled->setDrawColor(0);
  oled->drawLine(64, 51, 64, 55); // Center groove
  oled->setDrawColor(1);
}

// 4. DIZZY / OVERWHELMED (@ @ or X X with zigzag mouth)
void renderDizzy(uint32_t now) {
  int cy = 30;
  int leftCx  = 64 - 24;
  int rightCx = 64 + 24;
  int angle = (now / 25) % 360;

  // Spinning crosses
  float rad = angle * 0.0174533f;
  float c = cosf(rad) * 12.0f;
  float s = sinf(rad) * 12.0f;

  for (int cx : {leftCx, rightCx}) {
    oled->drawCircle(cx, cy, 15);
    oled->drawLine(cx - (int)c, cy - (int)s, cx + (int)c, cy + (int)s);
    oled->drawLine(cx + (int)s, cy - (int)c, cx - (int)s, cy + (int)c);
  }

  // Wavy mouth
  int mx = 50, my = 54;
  for (int i = 0; i < 28; i++) {
    int waveY = my + (int)(sinf((now * 0.015f) + i * 0.4f) * 2.5f);
    oled->drawPixel(mx + i, waveY);
    oled->drawPixel(mx + i, waveY + 1);
  }
}

// 5. HEART EYES (IN LOVE)
void renderHeartEyes(uint32_t now) {
  // Beating pulse effect
  float beat = sinf(now * 0.008f);
  int heartSize = 22 + (int)(beat * 5.0f);

  drawHeart(64 - 25, 30, heartSize);
  drawHeart(64 + 25, 30, heartSize);

  // Big happy open smile (D)
  oled->drawCircle(64, 50, 8);
  oled->setDrawColor(0);
  oled->drawBox(54, 40, 20, 10); // Cut top off to make open smile
  oled->setDrawColor(1);
  oled->drawLine(56, 50, 72, 50);
}

// 6. SASSY POUT (Cute angry baby)
void renderPout(uint32_t now) {
  int eyeW = 28, eyeH = 26;
  int leftX  = 64 - 14 - eyeW;
  int rightX = 64 + 14;
  int y = 24;

  oled->drawRBox(leftX, y, eyeW, eyeH, 5);
  oled->drawRBox(rightX, y, eyeW, eyeH, 5);

  // Slanted sharp eyelids cut from top inner corners
  oled->setDrawColor(0);
  oled->drawTriangle(leftX - 1, y - 1, leftX + eyeW + 1, y - 1, leftX + eyeW + 1, y + 14);
  oled->drawTriangle(rightX - 1, y - 1, rightX + eyeW + 1, y - 1, rightX - 1, y + 14);

  // White angry glare pupils
  oled->drawDisc(leftX + 10, y + 16, 4);
  oled->drawDisc(rightX + eyeW - 10, y + 16, 4);
  oled->setDrawColor(1);

  // Cute inverted pout mouth :<
  oled->drawLine(59, 56, 64, 52);
  oled->drawLine(64, 52, 69, 56);
}

// 7. SLEEPY WITH FLOATING Zzz
void renderSleepy(uint32_t now) {
  int cy = 34;
  // Closed sleeping crescent eyes: v  v
  oled->drawArc(64 - 24, cy, 12, 45, 135);
  oled->drawArc(64 - 24, cy - 1, 12, 45, 135);
  oled->drawArc(64 + 24, cy, 12, 45, 135);
  oled->drawArc(64 + 24, cy - 1, 12, 45, 135);

  // Tiny snoring bubble mouth 'o'
  float breath = sinf(now * 0.003f);
  int r = 2 + (int)(breath * 1.5f);
  if (r < 1) r = 1;
  oled->drawCircle(64, 54, r);

  // Floating animated comic 'Z' letters
  oled->setFont(u8g2_font_6x10_tr);
  for (int i = 0; i < 3; i++) {
    uint32_t zTime = now + (i * 900);
    int progress = (zTime / 22) % 60; // 0 to 60 px up
    int zX = 76 + (i * 12) + (int)(sinf(progress * 0.15f) * 4);
    int zY = 52 - progress;
    if (zY > 4 && zY < 60) {
      if (i == 0) oled->setFont(u8g2_font_5x8_tr);
      else if (i == 1) oled->setFont(u8g2_font_6x10_tr);
      else oled->setFont(u8g2_font_7x14_tr);
      oled->drawStr(zX, zY, "Z");
    }
  }
}

// 8. SNEEZE ("ACHOO!" screen earthquake)
void renderSneeze(uint32_t now) {
  uint32_t elapsed = now - sneezeStart;

  if (elapsed < 1400) {
    // Stage 1: Build-up, eyes tight shut > <
    oled->drawLine(64 - 36, 26, 64 - 18, 34);
    oled->drawLine(64 - 36, 42, 64 - 18, 34);

    oled->drawLine(64 + 36, 26, 64 + 18, 34);
    oled->drawLine(64 + 36, 42, 64 + 18, 34);

    // Quivering nervous mouth
    oled->drawCircle(64, 51, 3);
  } else if (elapsed < 2300) {
    // Stage 2: ACHOO! Explosion & Screen Earthquake
    int shakeX = random(-4, 5);
    int shakeY = random(-3, 4);

    oled->setFont(u8g2_font_logisoso16_tr);
    oled->drawStr(14 + shakeX, 36 + shakeY, "ACHOO!");

    // Comic starbursts
    oled->drawCircle(64 + shakeX, 48 + shakeY, 12);
    oled->drawLine(20 + shakeX, 10, 30 + shakeX, 18);
    oled->drawLine(108 + shakeX, 12, 98 + shakeX, 19);
  } else if (elapsed < 3400) {
    // Stage 3: Dazed after-sneeze (dizzy eyes)
    oled->drawCircle(64 - 22, 32, 10);
    oled->drawCircle(64 + 22, 32, 10);
    oled->drawPixel(64 - 22, 32);
    oled->drawPixel(64 + 22, 32);
    oled->drawLine(60, 52, 68, 52); // Flat mouth
  } else {
    // Sneeze completed, return to normal
    curMood = MOOD_NORMAL;
    moodTimer = now;
  }
}

// ------------------------------------------------------------- Master Render
void render(uint32_t now) {
  oled->clearBuffer();

  switch (curMood) {
    case MOOD_NORMAL:   renderNormal(now); break;
    case MOOD_SIDE_EYE: renderSideEye(now); break;
    case MOOD_DERP:     renderDerp(now); break;
    case MOOD_DIZZY:    renderDizzy(now); break;
    case MOOD_HEARTS:   renderHeartEyes(now); break;
    case MOOD_POUT:     renderPout(now); break;
    case MOOD_SLEEPY:   renderSleepy(now); break;
    case MOOD_SNEEZE:   renderSneeze(now); break;
    default:            renderNormal(now); break;
  }

  // Draw speech bubble if active
  if (showSpeechBubble) {
    if (now - speechStartMs < SPEECH_DURATION) {
      drawSpeechBubble(FUNNY_QUOTES[currentQuoteIdx]);
    } else {
      showSpeechBubble = false;
      nextSpeechMs = now + random(7000, 16000); // Next funny remark in 7-16s
    }
  }

  oled->sendBuffer();
}

// --------------------------------------------------------------- Mood Switch
void setMood(Mood m, uint32_t now) {
  curMood = m;
  moodTimer = now;
  blinking = false;
  blinkFactor = 1.0f;

  if (m == MOOD_SNEEZE) {
    sneezeStart = now;
  }

  Serial.printf("[Minimo] New Mood: %s\n", MOOD_NAMES[m]);
}

void triggerSpeechBubble(uint32_t now) {
  currentQuoteIdx = random(TOTAL_QUOTES);
  showSpeechBubble = true;
  speechStartMs = now;
  Serial.printf("[Minimo] Saying: \"%s\"\n", FUNNY_QUOTES[currentQuoteIdx]);
}

// ----------------------------------------------------------- Serial & Button
void handleInputs(uint32_t now) {
  // Serial Commands (type 1..8 in Serial Monitor)
  while (Serial.available()) {
    char c = Serial.read();
    if (c >= '1' && c <= '8') {
      autoCycle = false;
      setMood((Mood)(c - '1'), now);
    } else if (c == 'a' || c == 'A') {
      autoCycle = true;
      Serial.println("[Minimo] Auto Cycle Enabled!");
    } else if (c == 's' || c == 'S') {
      triggerSpeechBubble(now);
    } else if (c == 'b' || c == 'B') {
      nextBlink = now;
    }
  }

  // Hardware push button (active LOW)
  static bool lastBtn = HIGH;
  static uint32_t lastDebounce = 0;
  bool btnState = digitalRead(BTN_PIN);
  if (btnState != lastBtn && (now - lastDebounce > 150)) {
    lastDebounce = now;
    lastBtn = btnState;
    if (btnState == LOW) {
      // Button tapped: switch to next mood and speak!
      setMood((Mood)((curMood + 1) % MOOD_COUNT), now);
      if (random(100) < 60) triggerSpeechBubble(now);
    }
  }
}

// --------------------------------------------------- Auto I2C Pin Detection
bool probeOled(int sda, int scl, uint8_t &addr) {
  if (!Wire.begin(sda, scl, 100000)) return false;
  Wire.setTimeOut(25);
  bool found = false;
  for (uint8_t a : {0x3C, 0x3D}) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      addr = a;
      found = true;
      break;
    }
  }
  Wire.end();
  return found;
}

// -------------------------------------------------------- Cute Intro Sequence
void drawCenteredStr(int y, const uint8_t *font, const char *str) {
  oled->setFont(font);
  int w = oled->getStrWidth(str);
  int x = (128 - w) / 2;
  if (x < 0) x = 0;
  oled->drawStr(x, y, str);
}

void playIntroAnimation() {
  Serial.println("[Minimo] Playing cute intro for Sudarsan...");

  // Phase 1: Waking up (eyes slowly opening)
  for (int h = 2; h <= 28; h += 2) {
    oled->clearBuffer();
    int y = 32 - h / 2;
    oled->drawRBox(64 - 14 - 28, y, 28, h, 6);
    oled->drawRBox(64 + 14, y, 28, h, 6);
    if (h > 12) {
      oled->setDrawColor(0);
      oled->drawDisc(64 - 14 - 8, y + 6, 3);
      oled->drawDisc(64 + 14 + 20, y + 6, 3);
      oled->setDrawColor(1);
    }
    // gentle smile
    oled->drawArc(64, 54, 5, 180, 360);
    oled->sendBuffer();
    delay(30);
  }
  delay(350);

  // Phase 2: "Hello, I'm Minimo!"
  uint32_t introStart = millis();
  while (millis() - introStart < 2500) {
    uint32_t t = millis() - introStart;
    float bounce = sinf(t * 0.008f) * 2.0f;

    oled->clearBuffer();
    // Cute decorative rounded border
    oled->drawRFrame(3, 3, 122, 58, 6);
    oled->drawRFrame(5, 5, 118, 54, 4);

    // Little corner sparkle dots
    oled->drawPixel(9, 9);
    oled->drawPixel(118, 9);
    oled->drawPixel(9, 54);
    oled->drawPixel(118, 54);

    drawCenteredStr(20 + (int)bounce, u8g2_font_6x10_tr, "HELLO! I'M");
    drawCenteredStr(36 + (int)bounce, u8g2_font_7x14B_tr, "* MINIMO *");
    drawCenteredStr(51 + (int)bounce, u8g2_font_6x10_tr, "( >  ^  < )");

    oled->sendBuffer();
    delay(20);
  }

  // Phase 3: "Sudarsan's Buddy!"
  introStart = millis();
  while (millis() - introStart < 2800) {
    uint32_t t = millis() - introStart;
    float beat = fabsf(sinf(t * 0.007f));
    int heartSize = 12 + (int)(beat * 5.0f);

    oled->clearBuffer();
    oled->drawRFrame(3, 3, 122, 58, 6);
    oled->drawRFrame(5, 5, 118, 54, 4);

    drawCenteredStr(19, u8g2_font_6x10_tr, "SUDARSAN'S");
    drawCenteredStr(34, u8g2_font_7x14B_tr, "BEST BUDDY!");

    // Two beating cartoon hearts flanking cute text
    drawHeart(36, 47, heartSize);
    drawHeart(92, 47, heartSize);
    drawCenteredStr(50, u8g2_font_6x10_tr, "<3  <3");

    oled->sendBuffer();
    delay(20);
  }

  // Phase 4: Happy Wink & Let's Go!
  oled->clearBuffer();
  // Left eye open with shine
  oled->drawRBox(64 - 14 - 28, 18, 28, 28, 7);
  oled->setDrawColor(0);
  oled->drawDisc(64 - 14 - 8, 24, 3);
  oled->setDrawColor(1);
  // Right eye winking curve
  oled->drawLine(64 + 14, 32, 64 + 14 + 14, 25);
  oled->drawLine(64 + 14 + 14, 25, 64 + 14 + 28, 32);
  // Big open smile
  oled->drawArc(64, 52, 7, 180, 360);
  drawCenteredStr(12, u8g2_font_5x8_tr, "LET'S GO!");
  oled->sendBuffer();
  delay(1000);
}

// --------------------------------------------------------------------- Setup
void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("\n======================================");
  Serial.println("  MINIMO KEYCHAIN - Starting Up!  ");
  // Configure button
  pinMode(BTN_PIN, INPUT_PULLUP);
  randomSeed(esp_random());

  Serial.println("[Init] Scanning for OLED on I2C pins...");

  // Auto-detect I2C pins for ESP32-C3 SuperMini
  const int pairs[][2] = {
    {8, 9}, {9, 8},   // Default C3 I2C pins
    {4, 5}, {5, 4},
    {5, 6}, {6, 5},
    {6, 7}, {7, 6},
    {2, 3}, {3, 2},
    {0, 1}, {1, 0},
    {20, 21}, {21, 20}
  };

  int sdaPin = 8, sclPin = 9;
  uint8_t oledAddr = 0x3C;
  bool detected = false;

  for (auto &pair : pairs) {
    Serial.printf("  Testing SDA=%d, SCL=%d... ", pair[0], pair[1]);
    if (probeOled(pair[0], pair[1], oledAddr)) {
      sdaPin = pair[0];
      sclPin = pair[1];
      detected = true;
      Serial.printf("FOUND OLED at 0x%02X!\n", oledAddr);
      break;
    } else {
      Serial.println("No ACK");
    }
  }

  if (detected) {
    Serial.printf("[OLED] Found at 0x%02X on SDA=%d, SCL=%d\n", oledAddr, sdaPin, sclPin);
  } else {
    Serial.println("[OLED] Not detected automatically. Defaulting to SDA=8, SCL=9. Check wiring!");
  }

  // Initialize U8g2 driver
#if USE_SH1106_1_3_INCH
  Serial.println("[OLED] Initializing 1.3\" SH1106 display...");
  oled = new U8G2_SH1106_128X64_NONAME_F_HW_I2C(U8G2_R0, U8X8_PIN_NONE, sclPin, sdaPin);
#else
  Serial.println("[OLED] Initializing 0.96\" SSD1306 display...");
  oled = new U8G2_SSD1306_128X64_NONAME_F_HW_I2C(U8G2_R0, U8X8_PIN_NONE, sclPin, sdaPin);
#endif

  oled->setI2CAddress(oledAddr << 1);
  oled->setBusClock(400000); // 400kHz Fast I2C for snappy FPS
  oled->begin();

  // Play cute intro sequence on boot!
  playIntroAnimation();

  uint32_t now = millis();
  moodTimer    = now;
  nextBlink    = now + 1200;
  nextGazeChange = now + 1500;
  nextSpeechMs = now + 4000;

  setMood(MOOD_NORMAL, now);

  Serial.println("\nCommands via Serial Monitor:");
  Serial.println("  1..8 : Change expression directly");
  Serial.println("  'a'  : Toggle auto cycle");
  Serial.println("  's'  : Show funny speech bubble");
  Serial.println("  'b'  : Trigger instant blink");
}

// ---------------------------------------------------------------------- Loop
void loop() {
  uint32_t now = millis();

  // Read button and Serial commands
  handleInputs(now);

  // Auto-switch mood every few seconds if autoCycle is enabled
  if (autoCycle && (curMood != MOOD_SNEEZE)) {
    if (now - moodTimer > moodDuration) {
      // Pick next mood (random or sequence)
      Mood next = (Mood)((curMood + 1) % MOOD_COUNT);
      // Give sneeze a lower chance so it's a funny surprise
      if (next == MOOD_SNEEZE && random(100) > 30) {
        next = (Mood)((next + 1) % MOOD_COUNT);
      }
      setMood(next, now);
      moodDuration = random(4000, 7000);
    }
  }

  // Trigger random funny speech bubble
  if (!showSpeechBubble && (int32_t)(now - nextSpeechMs) >= 0) {
    triggerSpeechBubble(now);
  }

  // Update animations
  updateBlinking(now);
  updateGaze(now);

  // Draw current frame to screen
  render(now);

  // Short yield for ESP32 watchdog and thermal stability
  delay(20);
}
