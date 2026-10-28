/*
 * TARS - AM312 motion sensor bench test on the pir_test plate (tars4.scad).
 *
 * Compares the four mounting positions of the plate:
 *   e  : cap inserted from the outside, dome protrudes 5.7 mm
 *   1  : glued from the inside, hole 10.5 mm, dome protrudes ~0.47 mm
 *   2  : glued from the inside, hole 11.0 mm, dome protrudes ~1.01 mm
 *   3  : glued from the inside, hole 11.5 mm, dome protrudes ~1.75 mm
 *
 * Wiring (AM312 breakout 10.25 x 8.10 mm, pins VIN / OUT / GND):
 *
 *     AM312            Pro Micro
 *     -----            ---------
 *     VIN  ----------- VCC   (5 V on the 16 MHz board, 3.3 V on the 8 MHz one;
 *                             the AM312 accepts 2.7-12 V)
 *     OUT  ----------- D2    (PD1 / INT1, no pull-up)
 *     GND  ----------- GND
 *
 *     Board RX LED (pin 17, active low) mirrors OUT.
 *
 * Levels: OUT is push-pull, ~3.3 V high (internal regulator). On a 5 V Pro
 * Micro VIH min = 0.6 x VCC = 3.0 V: it works, with little margin. If edges
 * are missed on the 5 V board, run it from 3.3 V or add a level shifter.
 *
 * Sensor behaviour: OUT stays high ~2 s after a detection; 10-60 s warm-up
 * after power-up, during which edges are ignored (WARMUP_MS).
 *
 * Serial commands (115200 baud, one letter, no Enter needed):
 *   e / 1 / 2 / 3  select the configuration under test (prints the summary
 *                  of the previous one)
 *   r              reset the counters of the current configuration
 *   s              print the summary of all configurations
 *   w              skip the remaining warm-up
 *   ?              help
 *
 * Log lines are CSV, prefixed so they can be grepped:
 *   EVT,<ms>,<cfg>,RISE,<count>
 *   EVT,<ms>,<cfg>,FALL,<count>,<high_ms>
 * Distance and angle are measured by hand: the summary leaves blanks for them.
 *
 * Note: the Arduino core also flashes the RX LED on USB traffic, so a typed
 * command can blink it for a few ms.
 */

#include <Arduino.h>

static const uint8_t PIN_PIR = 2;        // INT1
static const uint8_t PIN_LED = 17;       // RX LED, active low
static const uint32_t WARMUP_MS = 30000;
static const uint32_t SERIAL_WAIT_MS = 3000;

struct Config {
  char key;
  const char *label;
  uint16_t detections;
  uint32_t total_high_ms;
  uint32_t min_high_ms;
  uint32_t max_high_ms;
  uint32_t started_ms;
};

static Config configs[] = {
  {'e', "outside cap, dome +5.7 mm", 0, 0, 0, 0, 0},
  {'1', "inside, hole 10.5 mm, dome +0.47 mm", 0, 0, 0, 0, 0},
  {'2', "inside, hole 11.0 mm, dome +1.01 mm", 0, 0, 0, 0, 0},
  {'3', "inside, hole 11.5 mm, dome +1.75 mm", 0, 0, 0, 0, 0},
};
static const uint8_t CONFIG_COUNT = sizeof(configs) / sizeof(configs[0]);

// Edge queue filled by the ISR, drained by loop().
struct Edge {
  uint32_t ms;
  uint8_t level;
};
static const uint8_t QUEUE_SIZE = 16;    // power of two
static volatile Edge queue[QUEUE_SIZE];
static volatile uint8_t queue_head = 0;
static volatile uint8_t queue_overflow = 0;
static volatile uint8_t queue_tail = 0;

static Config *current = &configs[0];
static bool warming_up = true;
static uint32_t warmup_start_ms = 0;
static uint32_t rise_ms = 0;
static bool high = false;

static void on_pir_change() {
  uint8_t next = (queue_head + 1) & (QUEUE_SIZE - 1);
  if (next == queue_tail) {
    queue_overflow = 1;
    return;
  }
  queue[queue_head].ms = millis();
  queue[queue_head].level = digitalRead(PIN_PIR);
  queue_head = next;
}

static void reset_config(Config *c) {
  c->detections = 0;
  c->total_high_ms = 0;
  c->min_high_ms = 0;
  c->max_high_ms = 0;
  c->started_ms = millis();
}

static void print_summary(const Config *c) {
  Serial.print(F("SUM,"));
  Serial.print(c->key);
  Serial.print(F(",\""));
  Serial.print(c->label);
  Serial.print(F("\",detections="));
  Serial.print(c->detections);
  Serial.print(F(",high_min="));
  Serial.print(c->min_high_ms);
  Serial.print(F(",high_avg="));
  Serial.print(c->detections ? c->total_high_ms / c->detections : 0);
  Serial.print(F(",high_max="));
  Serial.print(c->max_high_ms);
  Serial.print(F(",duration_s="));
  Serial.print((millis() - c->started_ms) / 1000);
  Serial.println(F(",distance_cm=____,angle_deg=____"));
}

static void print_help() {
  Serial.println(F("# commands: e/1/2/3 select config, r reset, s summary, w skip warm-up, ? help"));
  for (uint8_t i = 0; i < CONFIG_COUNT; i++) {
    Serial.print(F("#   "));
    Serial.print(configs[i].key);
    Serial.print(F(" = "));
    Serial.println(configs[i].label);
  }
}

static void print_current() {
  Serial.print(F("CFG,"));
  Serial.print(millis());
  Serial.print(',');
  Serial.print(current->key);
  Serial.print(F(",\""));
  Serial.print(current->label);
  Serial.println('"');
}

static void end_warmup() {
  warming_up = false;
  noInterrupts();
  queue_tail = queue_head;               // drop warm-up edges
  queue_overflow = 0;
  interrupts();
  high = digitalRead(PIN_PIR);
  rise_ms = millis();
  for (uint8_t i = 0; i < CONFIG_COUNT; i++) reset_config(&configs[i]);
  Serial.print(F("# warm-up done, OUT is "));
  Serial.println(high ? F("HIGH (pulse in progress, not counted)") : F("LOW"));
  print_current();
}

static void handle_command(char cmd) {
  for (uint8_t i = 0; i < CONFIG_COUNT; i++) {
    if (configs[i].key == cmd) {
      if (current != &configs[i]) {
        print_summary(current);
        current = &configs[i];
        reset_config(current);
      }
      print_current();
      return;
    }
  }
  switch (cmd) {
    case 'r':
      reset_config(current);
      Serial.print(F("# reset "));
      Serial.println(current->key);
      break;
    case 's':
      for (uint8_t i = 0; i < CONFIG_COUNT; i++) print_summary(&configs[i]);
      break;
    case 'w':
      if (warming_up) end_warmup();
      break;
    case '?':
    case 'h':
      print_help();
      break;
    default:
      break;                             // ignore CR, LF and the rest
  }
}

static void handle_edge(const Edge &edge) {
  if (edge.level && !high) {
    high = true;
    rise_ms = edge.ms;
    current->detections++;
    Serial.print(F("EVT,"));
    Serial.print(edge.ms);
    Serial.print(',');
    Serial.print(current->key);
    Serial.print(F(",RISE,"));
    Serial.println(current->detections);
  } else if (!edge.level && high) {
    high = false;
    uint32_t high_ms = edge.ms - rise_ms;
    current->total_high_ms += high_ms;
    if (current->min_high_ms == 0 || high_ms < current->min_high_ms) current->min_high_ms = high_ms;
    if (high_ms > current->max_high_ms) current->max_high_ms = high_ms;
    Serial.print(F("EVT,"));
    Serial.print(edge.ms);
    Serial.print(',');
    Serial.print(current->key);
    Serial.print(F(",FALL,"));
    Serial.print(current->detections);
    Serial.print(',');
    Serial.println(high_ms);
  }
  // Same level twice: a glitch shorter than the ISR latency, nothing to log.
}

void setup() {
  pinMode(PIN_PIR, INPUT);               // AM312 OUT is push-pull, no pull-up
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);           // off

  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < SERIAL_WAIT_MS) {}

  Serial.println(F("# TARS AM312 test - pir_test plate"));
  print_help();

  attachInterrupt(digitalPinToInterrupt(PIN_PIR), on_pir_change, CHANGE);
  warmup_start_ms = 0;                   // the sensor was powered at reset
}

void loop() {
  uint32_t now = millis();

  digitalWrite(PIN_LED, digitalRead(PIN_PIR) ? LOW : HIGH);

  while (Serial.available()) handle_command(Serial.read());

  if (warming_up) {
    static uint32_t last_tick = 0;
    if (now - warmup_start_ms >= WARMUP_MS) {
      end_warmup();
    } else if (now - last_tick >= 5000 || last_tick == 0) {
      last_tick = now ? now : 1;
      Serial.print(F("# warm-up, "));
      Serial.print((WARMUP_MS - (now - warmup_start_ms)) / 1000);
      Serial.println(F(" s left (w to skip)"));
    }
    return;
  }

  if (queue_overflow) {
    queue_overflow = 0;
    Serial.println(F("# WARN edge queue overflow"));
  }

  while (queue_tail != queue_head) {
    Edge edge;
    noInterrupts();
    edge.ms = queue[queue_tail].ms;
    edge.level = queue[queue_tail].level;
    interrupts();
    queue_tail = (queue_tail + 1) & (QUEUE_SIZE - 1);
    handle_edge(edge);
  }
}
