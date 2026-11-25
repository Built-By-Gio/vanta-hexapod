// VANTA one-leg walk test: Arduino + PCA9685.
// Servos stay OFF at boot. Find each joint's home pulse (femur level, tibia straight down) with the jog keys,
// paste the printed numbers into HOME_US, re-upload, then walk. Walking is small offsets from home.
// Serial Monitor at 115200, "No line ending":
//   1/2/3 = pick coxa/femur/tibia (it powers on at its HOME_US)   + / - = 10us   ] / [ = 50us
//   p = print HOME_US   h = all joints home   t = test directions   w = walk   x = all off
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm(0x40);

const uint8_t CH[3] = {15, 14, 13};          // coxa, femur, tibia
int HOME_US[3] = {1500, 1500, 1500};         // paste the 'p' output here
const float SIGN[3] = {-1, 1, 1};            // a joint going the wrong way in 't': flip its sign
const float US_PER_DEG = 2000.0 / 180.0;
const float LO[3] = {-35, -80, -52}, HI[3] = {35, 85, 73};

const float COXA = 68.0, FEMUR = 76.7, TIBIA = 101.0;
const float HOME_X = COXA + FEMUR, HOME_Z = -TIBIA;
const float STRIDE = 40.0, LIFT = 25.0, CYCLE_MS = 1200, RAMP_MS = 1000;
const char *NAME[3] = {"coxa", "femur", "tibia"};

char mode = 'x';
int sel = -1;
unsigned long t0;
float amp = 0;   // walk size: ramps 0 -> 1 into a walk and 1 -> 0 back out, so the leg never jumps

void writeJoint(int j, float deg) {
  deg = constrain(deg, LO[j], HI[j]);
  pwm.writeMicroseconds(CH[j], HOME_US[j] + SIGN[j] * deg * US_PER_DEG);
}

void off(int j) {
  pwm.setPWM(CH[j], 0, 4096);
}

bool ik(float x, float y, float z, float out[3]) {
  float dr = hypot(x, y) - COXA;
  float reach = hypot(dr, z);
  float k = (FEMUR * FEMUR + reach * reach - TIBIA * TIBIA) / (2 * FEMUR * reach);
  if (k < -1 || k > 1) return false;
  float femur = atan2(z, dr) + acos(k);
  float kr = FEMUR * cos(femur), kz = FEMUR * sin(femur);
  out[0] = degrees(atan2(y, x));
  out[1] = degrees(femur);
  out[2] = degrees(femur - PI / 2 - atan2(z - kz, dr - kr));
  return true;
}

void footAt(float x, float y, float z) {
  float a[3];
  if (!ik(x, y, z, a)) return;
  for (int j = 0; j < 3; j++) writeJoint(j, a[j]);
}

void printHome() {
  Serial.print("int HOME_US[3] = {");
  Serial.print(HOME_US[0]); Serial.print(", ");
  Serial.print(HOME_US[1]); Serial.print(", ");
  Serial.print(HOME_US[2]); Serial.println("};");
}

void walkStep() {
  float p = fmod((millis() - t0) / CYCLE_MS, 1.0);
  float y, z = HOME_Z;
  if (p < 0.5) {
    y = STRIDE / 2 - STRIDE * (p * 2);
  } else {
    float h = p * 2 - 1;
    y = -STRIDE / 2 + STRIDE * h * h * (3 - 2 * h);
    z += LIFT * sin(PI * h);
  }
  footAt(HOME_X, y * amp, HOME_Z + (z - HOME_Z) * amp);
}

// ease a walk back down to home (about RAMP_MS) before anything else moves the leg
void settle() {
  while (amp > 0) {
    amp = max(0.0f, amp - 20.0f / RAMP_MS);
    walkStep();
    delay(20);
  }
}

// one servo at a time: three MG995s starting together pull a current spike that glitches the others
void homeOneByOne() {
  for (int j = 0; j < 3; j++) {
    writeJoint(j, 0);
    delay(400);
  }
}

void testJoints() {
  const char *want[3] = {"coxa: leg should swing counterclockwise seen from above",
                         "femur: knee should LIFT",
                         "tibia: foot should swing IN toward the body"};
  homeOneByOne();
  for (int j = 0; j < 3; j++) {
    Serial.println(want[j]);
    for (float d = 0; d <= 15; d += 1) { writeJoint(j, d); delay(30); }
    delay(800);
    for (float d = 15; d >= 0; d -= 1) { writeJoint(j, d); delay(30); }
    delay(800);
  }
  Serial.println("done");
}

void setup() {
  Serial.begin(115200);
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(50);
  delay(10);
  for (int j = 0; j < 3; j++) off(j);
  Serial.println("servos OFF. 1/2/3 pick a joint, +/- [ ] jog, p print, h home, t test, w walk, x off");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c >= '1' && c <= '3') {
      settle();
      sel = c - '1';
      mode = 'j';
      writeJoint(sel, 0);
      Serial.print(NAME[sel]); Serial.print(" "); Serial.println(HOME_US[sel]);
    } else if (sel >= 0 && (c == '+' || c == '-' || c == ']' || c == '[')) {
      int step = (c == '+' || c == '-') ? 10 : 50;
      HOME_US[sel] = constrain(HOME_US[sel] + (c == '+' || c == ']' ? step : -step), 600, 2400);
      writeJoint(sel, 0);
      Serial.print(NAME[sel]); Serial.print(" "); Serial.println(HOME_US[sel]);
    } else if (c == 'p') {
      printHome();
    } else if (c == 't') {
      settle();
      testJoints();
      mode = 'h';
    } else if (c == 'h' || c == 'w' || c == 'x') {
      if (c == 'x') amp = 0;
      else if (mode != 'h' && mode != 'w') homeOneByOne();
      if (c == 'h') settle();                     // walk -> home eases out instead of jumping
      if (c == 'w' && mode != 'w') t0 = millis();  // 'w' while walking just keeps walking
      mode = c;
      Serial.println(mode);
      if (mode == 'x') for (int j = 0; j < 3; j++) off(j);
    }
  }

  if (mode == 'h') {
    for (int j = 0; j < 3; j++) writeJoint(j, 0);
  } else if (mode == 'w') {
    amp = min(1.0f, amp + 20.0f / RAMP_MS);
    walkStep();
  }

  delay(20);
}
