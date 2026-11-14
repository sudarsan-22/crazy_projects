/*
 * ESP32 Bluetooth Music Controller
 *
 * Hardware:
 *   - ESP32 NodeMCU 30-pin (WROOM)
 *   - 1.3" OLED display (SH1106 / SSD1306 I2C, 128x64)
 *   - KY-040 Rotary Encoder
 *   - Tactile push button (11x4.3mm)
 *
 * Behaviour:
 *   - Connects to iPhone as Bluetooth A2DP sink named "MusicCtrl"
 *   - Displays song title and artist via AVRCP metadata
 *   - Rotary encoder CW  → Volume up
 *   - Rotary encoder CCW → Volume down
 *   - 3 buttons          → Previous / Next / Play-Pause
 *
 * Libraries needed:
 *   - ESP32-A2DP by Phil Schatzmann  (github.com/pschatzmann/ESP32-A2DP)
 *   - U8g2 by Oliver Krause          (Arduino Library Manager)
 */

#include "BluetoothA2DPSink.h"
#include <U8g2lib.h>
#include <Wire.h>

// ─── Pin Definitions ──────────────────────────────────────────────────────────
// OLED I2C (default ESP32 I2C pins)
#define OLED_SDA  21
#define OLED_SCL  22

// KY-040 Rotary Encoder
#define ENC_CLK   34   // CLK  (input only pin — no internal pullup needed, KY-040 has it)
#define ENC_DT    35   // DT   (input only pin)
#define ENC_SW    32   // SW   (use as Play/Pause button)

// Extra buttons (all wired as INPUT_PULLUP, press -> LOW)
#define BTN_PREV  33
#define BTN_NEXT  25

// ─── OLED Setup ───────────────────────────────────────────────────────────────
// Set to 1 for most 1.3" OLED modules (SH1106), set to 0 for SSD1306 modules.
#define OLED_IS_SH1106 1

#if OLED_IS_SH1106
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE, OLED_SCL, OLED_SDA);
#else
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE, OLED_SCL, OLED_SDA);
#endif

// ─── A2DP ─────────────────────────────────────────────────────────────────────
BluetoothA2DPSink a2dp_sink;

// ─── State ────────────────────────────────────────────────────────────────────
String g_title  = "No song";
String g_artist = "Not connected";
bool   g_display_dirty = true;

// Encoder state
volatile int  enc_last_clk  = HIGH;
volatile long enc_debounce   = 0;

// Volume state (0..127 for AVRCP absolute volume)
uint8_t g_volume = 70;

// Button debounce
volatile long enc_sw_debounce  = 0;
volatile long btn_prev_debounce = 0;
volatile long btn_next_debounce = 0;

uint8_t detect_oled_address() {
  const uint8_t candidates[] = {0x3C, 0x3D};
  for (uint8_t i = 0; i < 2; i++) {
    Wire.beginTransmission(candidates[i]);
    if (Wire.endTransmission() == 0) {
      return candidates[i];
    }
  }
  return 0;
}

// ─── AVRCP Metadata Callback ──────────────────────────────────────────────────
void avrc_metadata_callback(uint8_t attr_id, const uint8_t* attr_text) {
  String value = String((char*)attr_text);
  switch (attr_id) {
    case ESP_AVRC_MD_ATTR_TITLE:
      g_title = value.length() > 0 ? value : "Unknown";
      g_display_dirty = true;
      break;
    case ESP_AVRC_MD_ATTR_ARTIST:
      g_artist = value.length() > 0 ? value : "";
      g_display_dirty = true;
      break;
    default:
      break;
  }
}

// ─── Connection State Callback ────────────────────────────────────────────────
void connection_state_callback(esp_a2d_connection_state_t state, void* obj) {
  if (state == ESP_A2D_CONNECTION_STATE_CONNECTED) {
    g_title  = "Connected";
    g_artist = "Play a song";
    g_display_dirty = true;
  } else if (state == ESP_A2D_CONNECTION_STATE_DISCONNECTED) {
    g_title  = "MusicCtrl";
    g_artist = "Waiting...";
    g_display_dirty = true;
  }
}

// ─── Display Helper ───────────────────────────────────────────────────────────
// Scrolls long text by truncating with ellipsis for now (simple approach)
String truncate(const String& s, uint8_t max_chars) {
  if (s.length() <= max_chars) return s;
  return s.substring(0, max_chars - 1) + char(0xBB); // »
}

void update_display() {
  u8g2.clearBuffer();

  // Top bar: Bluetooth icon area
  u8g2.setFont(u8g2_font_open_iconic_all_1x_t);
  u8g2.drawStr(0, 10, "\x80"); // Bluetooth glyph (code 0x80 in open_iconic)

  u8g2.setFont(u8g2_font_6x10_tf);
  u8g2.drawStr(14, 10, "MusicCtrl");

  // Divider
  u8g2.drawHLine(0, 13, 128);

  // Song title (larger font)
  u8g2.setFont(u8g2_font_7x13B_tf);
  String title_line = truncate(g_title, 17);
  u8g2.drawStr(0, 30, title_line.c_str());

  // Artist (smaller font)
  u8g2.setFont(u8g2_font_6x10_tf);
  String artist_line = truncate(g_artist, 20);
  u8g2.drawStr(0, 45, artist_line.c_str());

  // Bottom hint
  u8g2.setFont(u8g2_font_04b_03_tr);
  u8g2.drawStr(0, 62, "TURN=VOL | B:Pr Nx PP");

  u8g2.sendBuffer();
}

void show_startup_splash() {
  u8g2.clearBuffer();

  u8g2.setFont(u8g2_font_7x13B_tf);
  u8g2.drawStr(3, 24, "hello sudarsan");

  // Draw a small heart icon under the text.
  u8g2.drawDisc(56, 40, 5, U8G2_DRAW_ALL);
  u8g2.drawDisc(66, 40, 5, U8G2_DRAW_ALL);
  u8g2.drawTriangle(51, 42, 71, 42, 61, 56);

  u8g2.sendBuffer();
  delay(4000);
}

// Play/pause toggle state
bool is_playing = false;

void apply_volume_step(int delta) {
  // Keep a local absolute volume and send both commands for better phone compatibility.
  int next = (int)g_volume + delta * 3;
  if (next < 0) next = 0;
  if (next > 127) next = 127;
  g_volume = (uint8_t)next;

  if (delta > 0) {
    a2dp_sink.volume_up();
  } else {
    a2dp_sink.volume_down();
  }
  a2dp_sink.set_volume(g_volume);
  Serial.printf("Volume=%u\n", g_volume);
}

void toggle_play_pause() {
  if (is_playing) {
    a2dp_sink.pause();
    is_playing = false;
  } else {
    a2dp_sink.play();
    is_playing = true;
  }
}

// ─── Setup ────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // OLED
  Wire.begin(OLED_SDA, OLED_SCL);
  Wire.setClock(100000);
  delay(50);

  uint8_t oled_addr = detect_oled_address();
  if (oled_addr != 0) {
    // U8g2 expects 8-bit I2C address format.
    u8g2.setI2CAddress(oled_addr << 1);
    Serial.printf("OLED detected at 0x%02X\n", oled_addr);
  } else {
    Serial.println("OLED not detected on 0x3C/0x3D");
  }

  u8g2.begin();
  u8g2.setPowerSave(0);
  u8g2.setContrast(255);
  show_startup_splash();

  // Encoder pins
  pinMode(ENC_CLK, INPUT);
  pinMode(ENC_DT,  INPUT);
  pinMode(ENC_SW,  INPUT_PULLUP);
  enc_last_clk = digitalRead(ENC_CLK);

  // Extra buttons
  pinMode(BTN_PREV, INPUT_PULLUP);
  pinMode(BTN_NEXT, INPUT_PULLUP);

  // A2DP sink — no I2S output needed (we only want metadata + AVRCP control)
  // Disable audio data output — we only need AVRCP metadata and commands
  a2dp_sink.set_stream_reader(nullptr, false);   // disable I2S output
  a2dp_sink.set_avrc_metadata_callback(avrc_metadata_callback);
  a2dp_sink.set_avrc_metadata_attribute_mask(
    ESP_AVRC_MD_ATTR_TITLE | ESP_AVRC_MD_ATTR_ARTIST
  );
  a2dp_sink.set_on_connection_state_changed(connection_state_callback, nullptr);

  // Start A2DP with device name shown on iPhone
  a2dp_sink.start("MusicCtrl");
  a2dp_sink.set_volume(g_volume);

  // Initial display
  g_title  = "MusicCtrl";
  g_artist = "Waiting...";
  update_display();

  Serial.println("ESP32 Music Controller ready. Pair via Bluetooth as 'MusicCtrl'.");
}

// ─── Loop ─────────────────────────────────────────────────────────────────────
void loop() {
  long now = millis();

  // ── Rotary Encoder ──────────────────────────────────────────────────────────
  int clk_val = digitalRead(ENC_CLK);
  // Trigger on one edge only to avoid double counts and direction jitter.
  if (enc_last_clk == HIGH && clk_val == LOW && (now - enc_debounce) > 3) {
    enc_debounce = now;
    if (digitalRead(ENC_DT) != clk_val) {
      apply_volume_step(+1);
    } else {
      apply_volume_step(-1);
    }
  }
  enc_last_clk = clk_val;

  // ── Button: Play/Pause (encoder switch) ───────────────────────────────────
  static bool enc_sw_last = HIGH;
  bool enc_sw_now = digitalRead(ENC_SW);
  if (enc_sw_now == LOW && enc_sw_last == HIGH && (now - enc_sw_debounce) > 200) {
    enc_sw_debounce = now;
    toggle_play_pause();
    Serial.println("Play/Pause");
  }
  enc_sw_last = enc_sw_now;

  // ── Button: Previous ───────────────────────────────────────────────────────
  static bool btn_prev_last = HIGH;
  bool btn_prev_now = digitalRead(BTN_PREV);
  if (btn_prev_now == LOW && btn_prev_last == HIGH && (now - btn_prev_debounce) > 200) {
    btn_prev_debounce = now;
    a2dp_sink.previous();
    Serial.println("Previous");
  }
  btn_prev_last = btn_prev_now;

  // ── Button: Next ───────────────────────────────────────────────────────────
  static bool btn_next_last = HIGH;
  bool btn_next_now = digitalRead(BTN_NEXT);
  if (btn_next_now == LOW && btn_next_last == HIGH && (now - btn_next_debounce) > 200) {
    btn_next_debounce = now;
    a2dp_sink.next();
    Serial.println("Next");
  }
  btn_next_last = btn_next_now;

  // ── Refresh Display if needed ───────────────────────────────────────────────
  if (g_display_dirty) {
    g_display_dirty = false;
    update_display();
  }

  delay(1);//suadrsam
}