// VANTA servo check: goes through all 18 joints one at a time, says which one SHOULD move, and wiggles it.
// Write down any step where a different joint moves, or nothing moves.
// Prop the body up so the feet hang free: every servo is limp except the one being tested.
// Serial Monitor at 115200:  n next   b back   r repeat
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca1(0x40, Wire);    // driver 1: SDA 8 / SCL 9
Adafruit_PWMServoDriver pca2(0x40, Wire1);   // driver 2: SDA 4 / SCL 5

// same tables as vanta_hexapod_pad (channel map 2026-11-24).
// The names are where each leg physically is (front = the way it walks with the stick forward).
const char *WHERE[6] = {"FRONT LEFT", "MIDDLE LEFT", "BACK LEFT", "FRONT RIGHT", "MIDDLE RIGHT", "BACK RIGHT"};
const char *JOINT[3] = {"coxa (hip, swings the leg forward/back)", "femur (lifts the knee)", "tibia (the shin)"};
const uint8_t BOARD[6][3] = {{2, 2, 2}, {2, 2, 2}, {2, 2, 2}, {1, 1, 2}, {1, 1, 1}, {1, 1, 1}};   // the 2026-11-24 list was named facing the robot (camera side), so its left is the robot's right
const uint8_t CH[6][3] = {{0, 1, 2}, {4, 5, 3}, {7, 6, 8}, {0, 1, 15}, {3, 4, 5}, {6, 7, 8}};
const int HOME_US[6][3] = {{1500, 1550, 1050}, {1800, 1750, 1650}, {1400, 1370, 1650},
                           {1850, 1650, 1800}, {1650, 1300, 1950}, {1700, 1330, 1180}};

int step = 0;

Adafruit_PWMServoDriver &board(int leg, int j) { return BOARD[leg][j] == 1 ? pca1 : pca2; }

void allOff() {
  for (int ch = 0; ch < 16; ch++) { pca1.setPWM(ch, 0, 4096); pca2.setPWM(ch, 0, 4096); }
}

void test() {
  int leg = step / 3, j = step % 3, home = HOME_US[leg][j];
  allOff();
  Serial.printf("\n%2d/18  %s  %s\n       driver %d, channel %d\n", step + 1, WHERE[leg], JOINT[j], BOARD[leg][j], CH[leg][j]);
  board(leg, j).writeMicroseconds(CH[leg][j], home);
  delay(600);
  for (int i = 0; i < 3; i++) {
    board(leg, j).writeMicroseconds(CH[leg][j], home + 90);
    delay(350);
    board(leg, j).writeMicroseconds(CH[leg][j], home - 90);
    delay(350);
  }
  board(leg, j).writeMicroseconds(CH[leg][j], home);
  delay(400);
  allOff();
  Serial.println("       done. n next, b back, r repeat");
}

bool found(TwoWire &w) {
  w.beginTransmission(0x40);
  return w.endTransmission() == 0;
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Wire.begin(8, 9);
  Wire1.begin(4, 5);
  Serial.printf("\nVANTA servo check. driver 1 %s, driver 2 %s\n", found(Wire) ? "found" : "NOT FOUND", found(Wire1) ? "found" : "NOT FOUND");
  for (auto *p : {&pca1, &pca2}) {
    p->begin();
    p->setOscillatorFrequency(27000000);
    p->setPWMFreq(50);
  }
  delay(10);
  allOff();
  Serial.println("Body propped up, battery on. Send n to start.");
  step = -1;
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.read();
  if (c == 'n') step = min(step + 1, 17);
  else if (c == 'b') step = max(step - 1, 0);
  else if (c != 'r' || step < 0) return;
  test();
}
