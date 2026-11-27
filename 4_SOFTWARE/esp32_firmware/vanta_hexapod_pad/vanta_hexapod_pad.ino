// VANTA hexapod: ESP32-S3 + 2x PCA9685, driven by an Xbox Wireless controller (Bluepad32).
// Driver 1 (Wire,  SDA 8 / SCL 9): right legs, except the front-right tibia. Driver 2 (Wire1, SDA 4 / SCL 5): left legs + the front-right tibia.
// Start with the robot sitting: battery on the floor, legs spread out in a standing shape.
//
// Controller:
//   R2 power up and stand          L2 sit down and power off       Menu (≡) emergency: all servos off
//   left stick  walk + crab sideways        right stick  turn
//   hold LB + right stick  lean the body    hold RB  slow, precise walking
//   A wave   B dance   X bow   Y rear up and claw
//   during a move: the same button stops it, another move button switches to that move, left stick stops it
//   D-pad up/down body height, left/right top speed
//   click the right stick: switch the legs between the maths and the neural network
//   click the left stick: switch walking between the normal walk and the walk learned in the sim
//   hold LB + press A (standing still): climb mode on/off. Body goes up and leans back, legs step one at a time,
//   straight up as high as the joints allow, over, and straight down. Very slow. Forward/back and turn only, no moves.
//   in climb mode: A climbs one step. Line the front feet up about 3 cm from the step, press A, then HOLD the left stick
//   forward; let go to pause. Both front legs go up onto the step, the body pulls itself forward, then the other legs
//   follow one at a time. D-pad up/down sets the step height (10 mm a press).
//   View (the two squares): injured leg. all six -> rear-left out -> rear-right out -> all six
//   (learned and injured walks only go forward and back)
// Serial Monitor (115200, No line ending) over USB:
//   1-6 pick leg (1 front left, 2 middle left, 3 back left, 4 front right, 5 middle right, 6 back right), c/f/t pick joint, + - nudge 10us, ] [ nudge 50us,
//   n flip direction, e test +15 and back, p print arrays to paste
//   u stand, d sit, w/b/l/r walk, space stop, x off, v wave, g dance, o bow, q rear up
//   > < height, 9/0 step length, 7/8 foot lift, = _ faster/slower, m swap left/right, k maths/neural network
//   y learned walk on/off, i injured leg, h climb mode, a climb a step (space pauses, a resumes), space also stops a move
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <Bluepad32.h>
#include "ik_net.h"   // the leg network trained by train/train_ik.py
#include "walk_net.h" // the walks learned in train/vanta_sim.py

Adafruit_PWMServoDriver pca1(0x40, Wire);
Adafruit_PWMServoDriver pca2(0x40, Wire1);

const char *LEG[6] = {"FRONT LEFT", "MIDDLE LEFT", "BACK LEFT", "FRONT RIGHT", "MIDDLE RIGHT", "BACK RIGHT"};   // same order as MOUNT
const char *JOINT[3] = {"coxa", "femur", "tibia"};
// driver (1 or 2) and channel for {coxa, femur, tibia}, as plugged in on 2026-11-24
const uint8_t BOARD[6][3] = {{2, 2, 2}, {2, 2, 2}, {2, 2, 2}, {1, 1, 2}, {1, 1, 1}, {1, 1, 1}};   // the 2026-11-24 list was named facing the robot (camera side), so its left is the robot's right
const uint8_t CH[6][3] = {{0, 1, 2}, {4, 5, 3}, {7, 6, 8},
                          {0, 1, 15}, {3, 4, 5}, {6, 7, 8}};

// pulse for each joint in YOUR standing pose, set with the jog keys (1-6, c/f/t, + - ] [, then p)
int HOME_US[6][3] = {{1500, 1550, 1050}, {1800, 1750, 1650}, {1400, 1370, 1650},
                     {1850, 1650, 1800}, {1650, 1300, 1950}, {1700, 1330, 1180}};
int SIGN[6][3] = {{-1, 1, 1}, {-1, 1, 1}, {-1, 1, 1}, {-1, 1, 1}, {-1, 1, 1}, {-1, 1, 1}};

const float US_PER_DEG = 2000.0 / 180.0;
const float LO[3] = {-35, -80, -52}, HI[3] = {35, 85, 73};
const float COXA = 68.0, FEMUR = 76.7, TIBIA = 101.0;

// mount point (x forward, y left, mm) and the direction the leg points (deg)
const float MOUNT[6][3] = {{82, 57, 45}, {0, 71, 90}, {-82, 57, 135},
                           {82, -57, -45}, {0, -71, -90}, {-82, -57, -135}};
const float PHASE[6] = {0.5, 0, 0.5, 0, 0.5, 0};   // tripods: FR BR ML step first, then FL BL MR

// sitting: feet spread out, body low enough that the battery rests on the floor
const float SIT_REACH = 165.0, SIT_Z = -48.0;   // raise SIT_Z toward 0 if the servos strain while sitting
const float REACH = 145.0, STAND_Z = -82.5;
const float TURN_MM = 60;
float stride = 110, lift = 90;   // mm; 9/0 and 7/8 in the Serial Monitor change them live
bool mirror = false;             // m swaps left and right, for testing only
float height = 20;               // mm the body is held above your calibrated stand; D-pad up/down
const float TUCK_MS = 3000, RISE_MS = 5000, RAMP_MS = 600;
float cycle = 800;               // ms per step cycle with the stick all the way; D-pad left/right
const float SLOW_CYCLE = 1400;   // ms per step cycle with the stick barely pushed
float phase = 0;

char mode = 'x';   // x off, j jogging, i sitting, u standing up, d sitting down, w standing/walking, a animation, c climbing a step
int selLeg = 0, selJoint = -1;
float fwd = 0, side = 0, turn = 0, amp = 0;
bool moving = false, offAfterSit = false;
unsigned long t0;
float STAND_DEG[3];   // joint angles the leg math has at the standing pose; HOME_US is that pose

// body pose (mm, degrees) applied on top of the stand, and per-leg foot offsets, used by lean and the moves
float bX, bY, bZ, bRoll, bPitch, bYaw;
float oX[6], oY[6], oZ[6];
float leanR = 0, leanP = 0, leanTR = 0, leanTP = 0;
char anim = 0, pending = 0;
unsigned long animT0, cancelT0 = 0;   // cancelT0 set: the move is frozen at cancelAt and easing back to the stand
float cancelAt;
const float CANCEL_MS = 500;

bool climb = false;
float climbK = 0;       // 0 normal .. 1 climbing; the body eases into the climb pose over a second, standing still
// climb gait: one leg at a time (wave gait), so five feet are always down
const float CLIMB_HEIGHT = 45, CLIMB_REACH = 135, CLIMB_PITCH = 6, CLIMB_BACK = 0;   // mm, deg: body up and nose up. More pitch overstretches the front tibias
const float CLIMB_LIFT = 190, CLIMB_OUT = 25, CLIMB_STRIDE = 60;   // asks for 190 mm; each foot gets as high as its joints allow
const float CLIMB_DUTY = 5.0 / 6, CLIMB_CYCLE = 9000, CLIMB_SLOW = 18000;   // ms for all six legs to take a step
const float CLIMB_SLEW = 4;   // deg per 20 ms, about what an MG995 can follow under load
float climbPrev[6][3];
bool climbOn = false;   // climbPrev is valid

bool learned = false;   // walk with the network from the sim instead of the tripod maths
int legOut = -1;        // mount of the injured leg: -1 none, 2 rear-left, 5 rear-right
float tuck[6];          // 0 leg in use .. 1 leg folded up out of the way
bool settling = false;  // a leg is still folding or unfolding
bool sitQueued = false;
float gaitPh = 0;       // step cycles, runs backwards when walking backwards
const float NET_SLEW = 7;   // deg per 20 ms
float netPrev[6][3];
bool netOn = false;     // netPrev is valid

ControllerPtr pad = nullptr;

Adafruit_PWMServoDriver &board(int leg, int j) { return BOARD[leg][j] == 1 ? pca1 : pca2; }
int mnt(int leg) { return mirror ? (leg + 3) % 6 : leg; }

void writeJoint(int leg, int j, float deg) {
  deg = constrain(deg, LO[j], HI[j]);
  int us = HOME_US[leg][j] + SIGN[leg][j] * (deg - STAND_DEG[j]) * US_PER_DEG;
  board(leg, j).writeMicroseconds(CH[leg][j], constrain(us, 550, 2450));
}

void allOff() {
  for (int ch = 0; ch < 16; ch++) { pca1.setPWM(ch, 0, 4096); pca2.setPWM(ch, 0, 4096); }
}

bool useNet = false;   // false: joint angles from the trig below. true: from the neural network

void netIk(float lx, float ly, float z, float out[3]) {
  float in[3] = {lx / IK_IN_SCALE, ly / IK_IN_SCALE, z / IK_IN_SCALE}, h1[IK_H], h2[IK_H];
  for (int i = 0; i < IK_H; i++) {
    float s = IK_B1[i];
    for (int j = 0; j < 3; j++) s += IK_W1[i][j] * in[j];
    h1[i] = tanhf(s);
  }
  for (int i = 0; i < IK_H; i++) {
    float s = IK_B2[i];
    for (int j = 0; j < IK_H; j++) s += IK_W2[i][j] * h1[j];
    h2[i] = tanhf(s);
  }
  for (int i = 0; i < 3; i++) {
    float s = IK_B3[i];
    for (int j = 0; j < IK_H; j++) s += IK_W3[i][j] * h2[j];
    out[i] = s * IK_OUT_SCALE;
  }
}

bool ik(int m, float x, float y, float z, float out[3]) {
  float g = radians(MOUNT[m][2]);
  float dx = x - MOUNT[m][0], dy = y - MOUNT[m][1];
  float lx = dx * cos(g) + dy * sin(g), ly = -dx * sin(g) + dy * cos(g);
  if (useNet) { netIk(lx, ly, z, out); return true; }
  float dr = hypot(lx, ly) - COXA, reach = hypot(dr, z);
  float k = (FEMUR * FEMUR + reach * reach - TIBIA * TIBIA) / (2 * FEMUR * reach);
  if (k < -1 || k > 1) return false;
  float femur = atan2(z, dr) + acos(k);
  float kr = FEMUR * cos(femur), kz = FEMUR * sin(femur);
  out[0] = degrees(atan2(ly, lx));
  out[1] = degrees(femur);
  out[2] = degrees(femur - PI / 2 - atan2(z - kz, dr - kr));
  return true;
}

void neutral(int leg, float r, float &x, float &y) {
  int m = mnt(leg);
  float g = radians(MOUNT[m][2]);
  x = MOUNT[m][0] + r * cos(g);
  y = MOUNT[m][1] + r * sin(g);
}

// foot at a spot on the ground (wx, wy, wz) with the body moved/tilted by the current body pose
bool placeFoot(int leg, float wx, float wy, float wz, float *out = nullptr) {
  float px = wx - bX, py = wy - bY, pz = wz - bZ;
  float yw = radians(bYaw), pt = radians(bPitch), rl = radians(bRoll);
  float x1 = px * cos(yw) + py * sin(yw), y1 = -px * sin(yw) + py * cos(yw);
  float x2 = x1 * cos(pt) - pz * sin(pt), z2 = x1 * sin(pt) + pz * cos(pt);
  float y3 = y1 * cos(rl) + z2 * sin(rl), z3 = -y1 * sin(rl) + z2 * cos(rl);
  float a[3];
  if (!ik(mnt(leg), x2, y3, z3, a)) return false;
  if (out) { for (int j = 0; j < 3; j++) out[j] = a[j]; return true; }
  for (int j = 0; j < 3; j++) writeJoint(leg, j, a[j]);
  return true;
}

void footAt(int leg, float r, float z) {
  float x, y;
  neutral(leg, r, x, y);
  placeFoot(leg, x, y, z);
}

// one joint at a time: 18 MG995s starting together pull a spike that glitches the boards
void sitOneByOne() {
  float a[3], x, y;
  for (int leg = 0; leg < 6; leg++) {
    neutral(leg, SIT_REACH, x, y);
    ik(mnt(leg), x, y, SIT_Z, a);
    for (int j = 0; j < 3; j++) { writeJoint(leg, j, a[j]); delay(120); }
  }
}

void rumble(int ms) {
  if (pad && pad->isConnected()) pad->playDualRumble(0, ms, 0x60, 0x80);
}

void resetPose() {
  bX = bY = bZ = bRoll = bPitch = bYaw = 0;
  for (int l = 0; l < 6; l++) oX[l] = oY[l] = oZ[l] = 0;
}

void standUp() {
  offAfterSit = false;
  if (mode == 'w' || mode == 'u' || mode == 'a') return;
  resetPose();
  if (mode != 'i') sitOneByOne();
  mode = 'u'; t0 = millis();
  Serial.println("standing up");
}

void sitDown(bool thenOff) {
  if (mode != 'w') return;
  if (legOut >= 0 || settling || climbK > 0) {   // unfold the leg / leave the climb pose first, the loop sits after that
    legOut = -1; climb = false; moving = false; sitQueued = true; offAfterSit = thenOff;
    return;
  }
  moving = false; amp = 0; resetPose(); leanR = leanP = 0;
  offAfterSit = thenOff;
  mode = 'd'; t0 = millis();
  Serial.println("sitting down");
}

// stop the running move; next = a move to start straight after, or 0
void cancelAnim(char next) {
  if (mode != 'a' || cancelT0) return;
  cancelT0 = millis();
  cancelAt = (cancelT0 - animT0) / 1000.0;
  pending = next;
}

void startAnim(char a) {
  if (mode == 'a') { cancelAnim(a == anim ? 0 : a); return; }
  if (mode != 'w') return;
  if (legOut >= 0 || settling) { Serial.println("no moves with a leg out"); return; }
  if (climb || climbK > 0) { Serial.println("no moves in climb mode"); return; }
  moving = false;
  pending = a;   // starts once the legs have settled out of the walk
}

void toggleBrain() {
  useNet = !useNet;
  Serial.printf("brain: %s\n", useNet ? "NEURAL NETWORK" : "maths");
  rumble(useNet ? 400 : 100);
}

void toggleClimb() {
  if (mode != 'w' || amp > 0 || pending || learned || legOut >= 0 || settling) { Serial.println("climb: stand still on the normal walk first"); return; }
  climb = !climb;
  Serial.printf("climb: %s\n", climb ? "ON" : "off");
  rumble(climb ? 400 : 100);
}

bool fits(const float a[3]) {
  for (int j = 0; j < 3; j++) if (a[j] < LO[j] || a[j] > HI[j]) return false;
  return true;
}

void toggleLearned() {
  if (amp > 0 || climb) return;   // only while standing still, the two walks don't blend
  learned = !learned;
  Serial.printf("walk: %s\n", learned ? "LEARNED IN THE SIM" : "normal");
  rumble(learned ? 400 : 100);
}

void cycleLegOut() {
  if (mode != 'w' || amp > 0 || pending || climb) return;
  legOut = legOut == -1 ? 2 : legOut == 2 ? 5 : -1;
  moving = false;
  Serial.println(legOut == 2 ? "rear-left leg out" : legOut == 5 ? "rear-right leg out" : "all six legs");
  rumble(legOut < 0 ? 100 : 400);
}

// where we are in the step cycle -> how far each joint is from the stand (deg), per mount
void netWalk(const float *w, float cycles, float out[6][3]) {
  const float SWING[3] = {25, 30, 30};
  float a = TWO_PI * cycles, in[4] = {sinf(a), cosf(a), sinf(2 * a), cosf(2 * a)}, h[WALK_H];
  const float *w1 = w, *b1 = w1 + WALK_H * 4, *w2 = b1 + WALK_H, *b2 = w2 + 18 * WALK_H;
  for (int i = 0; i < WALK_H; i++) {
    float s = b1[i];
    for (int j = 0; j < 4; j++) s += w1[i * 4 + j] * in[j];
    h[i] = tanhf(s);
  }
  for (int i = 0; i < 18; i++) {
    float s = b2[i];
    for (int j = 0; j < WALK_H; j++) s += w2[i * WALK_H + j] * h[j];
    out[i / 3][i % 3] = tanhf(s) * SWING[i % 3];
  }
}

void changeHeight(float d) {
  height = constrain(height + d, -10.0f, 45.0f);
  Serial.printf("height %+.0f mm\n", height);
}

void changeSpeed(float d) {
  cycle = constrain(cycle + d, 350.0f, 1400.0f);
  Serial.printf("top-speed step time %.0f ms\n", cycle);
}

void off() {
  allOff(); mode = 'x'; moving = false; amp = 0; anim = pending = 0; cancelT0 = 0;
  legOut = -1; sitQueued = false;
  for (int m = 0; m < 6; m++) tuck[m] = 0;
  Serial.println("off");
}

void printArrays() {
  Serial.println("int HOME_US[6][3] = {");
  for (int l = 0; l < 6; l++)
    Serial.printf("  {%d, %d, %d}%s\n", HOME_US[l][0], HOME_US[l][1], HOME_US[l][2], l < 5 ? "," : "};");
  Serial.println("int SIGN[6][3] = {");
  for (int l = 0; l < 6; l++)
    Serial.printf("  {%d, %d, %d}%s\n", SIGN[l][0], SIGN[l][1], SIGN[l][2], l < 5 ? "," : "};");
}

void showSel() {
  if (selJoint < 0) { Serial.printf("%s selected, now c/f/t\n", LEG[selLeg]); return; }
  Serial.printf("%s %s  driver %d ch %d  HOME %d  SIGN %d\n", LEG[selLeg], JOINT[selJoint],
                BOARD[selLeg][selJoint], CH[selLeg][selJoint], HOME_US[selLeg][selJoint], SIGN[selLeg][selJoint]);
}

// ---------- the moves ----------
float smooth(float t) { t = constrain(t, 0.0f, 1.0f); return t * t * (3 - 2 * t); }
// 0 -> 1 over the first `e` seconds, 1 -> 0 over the last `e` seconds of a move lasting T
float env(float t, float T, float e) { return smooth(min(t / e, (T - t) / e)); }

float animLength(char a) { return a == 'v' ? 6.5 : a == 'g' ? 16 : a == 'o' ? 4 : 6.5; }

int legAt(int m) { return mirror ? (m + 3) % 6 : m; }   // which leg sits at physical mount m

// wave: body leans away, the front-right leg lifts high and waves three times
void wave(float t, int &skip, float wa[3]) {
  float e = env(t, 6.5, 1.0);
  bY = 25 * e; bX = -20 * e;
  int w = legAt(3);
  float x, y, a0[3];
  neutral(w, REACH, x, y);
  placeFoot(w, x, y, STAND_Z - height, a0);
  float up = smooth((t - 1.2) / 0.7) * (1 - smooth((t - 4.9) / 0.7));
  float flap = (t > 1.9 && t < 4.9) ? 25 * sin(TWO_PI * (t - 1.9)) : 0;
  wa[0] = a0[0] + flap * up;
  wa[1] = a0[1] + (65 - a0[1]) * up;
  wa[2] = a0[2] + (-35 - a0[2]) * up;
  skip = w;
}

// dance, on a 120 bpm beat: stomps with a head-bob, front legs pumping in the air,
// a kick that runs round the body one leg at a time, then crouch and pop up with the front legs thrown out
float beatHit(float t) {   // 0 -> 1 -> 0 inside each half-second beat: hits fast, recovers slower
  float p = fmod(t, 0.5f) / 0.5f;
  return p < 0.2 ? smooth(p / 0.2) : 1 - smooth((p - 0.2) / 0.6);
}

void dance(float t) {
  const int RING[6] = {0, 1, 2, 5, 4, 3};   // mounts in order round the body
  int fl = legAt(0), fr = legAt(3);
  if (t < 4) {
    float k = smooth(t / 0.5) * (1 - smooth((t - 3.6) / 0.4)), p = fmod(t, 0.5f) / 0.5f;
    int n = t / 0.5;
    bZ = -14 * beatHit(t) * k;
    for (int l = 0; l < 6; l++)
      if ((PHASE[l] == 0) == (n % 2 == 0)) oZ[l] = 35 * k * sin(PI * p);
  } else if (t < 8) {
    float u = t - 4, k = smooth(u / 0.6) * (1 - smooth((u - 3.4) / 0.6));
    float up = smooth((u - 0.4) / 0.5) * (1 - smooth((u - 3.1) / 0.5));
    bX = -30 * k; bPitch = -8 * k; bZ = -8 * beatHit(u) * k;
    oZ[fl] = oZ[fr] = up * (40 + 25 * beatHit(u));
    oY[fl] = 15 * up; oY[fr] = -15 * up;
  } else if (t < 12) {
    float u = t - 8, p = fmod(u, 0.5f) / 0.5f, kick = sin(PI * p);
    int m = RING[(int)(u / 0.5) % 6], l = legAt(m);
    float g = radians(MOUNT[m][2]);
    oZ[l] = 50 * kick; oX[l] = 30 * kick * cos(g); oY[l] = 30 * kick * sin(g);
    bX = -0.12 * MOUNT[m][0] * kick; bY = -0.12 * MOUNT[m][1] * kick;   // lean away from the kicking leg
  } else {
    float u = t - 12;
    float crouch = smooth(u / 1.2) * (1 - smooth((u - 1.4) / 0.25));
    float pop = smooth((u - 1.4) / 0.25) * (1 - smooth((u - 3.2) / 0.6));
    bZ = -25 * crouch + 12 * pop; bX = -30 * pop; bPitch = -8 * pop;
    float flick = 8 * sin(TWO_PI * 5 * u) * smooth((u - 1.8) / 0.3) * (1 - smooth((u - 3.0) / 0.3));
    oZ[fl] = oZ[fr] = 60 * pop + flick;
    oY[fl] = 25 * pop; oY[fr] = -25 * pop;
  }
}

// bow: nose down and forward, hold, back up
void bow(float t) {
  float e = env(t, 4, 1.0);
  bPitch = 14 * e; bZ = -15 * e; bX = 10 * e;
}

// rear up: body shifts back and tilts up, front legs lift and snap their claws together
void rearUp(float t) {
  float e = env(t, 6.5, 1.0);
  bX = -30 * e; bPitch = -8 * e;
  float up = smooth((t - 0.8) / 0.6) * (1 - smooth((t - 5.0) / 0.6));
  float claw = (t > 1.6 && t < 4.8) ? 20 * sin(TWO_PI * 1.5 * (t - 1.6)) : 0;
  int fl = legAt(0), fr = legAt(3);
  oZ[fl] = oZ[fr] = 60 * up;
  oY[fl] = -claw * up; oY[fr] = claw * up;
}

// ---------- climbing one step ----------
// Blind: the robot can't feel the step, so it assumes the edge is EDGE_GAP in front of the front feet and stepH tall.
// Feet are tracked in the world (mm, x forward from where the climb started, z up from the floor).
float stepH = 60;
const float EDGE_GAP = 25, ON_STEP = 35, CLEAR = 30, PULL = 60, STEP_STRIDE = 70, SWING_S = 1.5, HOLD_BACK = 15;
const float STEP_RIDE = 25, STEP_LEAN = 6, STEP_TILT = 0.5;   // body height (like the D-pad height), nose-up lean, and how much the body follows the slope of its feet
float fx[6], fy[6], fz[6], gnd[6];   // per mount: foot position and the ground height it stands on
float fromX[6], fromZ[6], toX[6], toZ[6];
float edgeX, bodyX, roundX, bodyZ, tilt, stepT, partT;
int part, swingIdx, rounds;
bool stepGo = false, lastRound = false, planned = false;
const int WAVE[6] = {5, 4, 3, 2, 1, 0};   // RR MR FR RL ML FL, back to front

float groundAt(float x) { return x > edgeX ? stepH : 0; }

void changeStep(float d) {
  stepH = constrain(stepH + d, 30.0f, 70.0f);   // past about 70 mm the legs on the floor and the legs on the step can't both reach
  Serial.printf("step height %.0f mm\n", stepH);
}

void startStep() {
  if (mode != 'w' || climbK < 1 || amp > 0) return;
  for (int m = 0; m < 6; m++) {
    float x, y;
    neutral(legAt(m), CLIMB_REACH, x, y);
    fx[m] = fromX[m] = toX[m] = x; fy[m] = y; fz[m] = gnd[m] = fromZ[m] = toZ[m] = 0;
  }
  edgeX = fx[0] + EDGE_GAP;
  bodyX = roundX = bodyZ = tilt = stepT = partT = 0;
  part = 0; swingIdx = 0; rounds = 0; lastRound = false; planned = false; stepGo = false;
  mode = 'c';
  Serial.printf("climbing a %.0f mm step: hold the stick forward\n", stepH);
  rumble(300);
}

// one foot from (fromX, fromZ) to (toX, toZ): straight up, over, straight down
void swingFoot(int m, float h) {
  float top = max(fromZ[m], toZ[m]) + CLEAR;
  fz[m] = h < 0.5 ? fromZ[m] + (top - fromZ[m]) * smooth(h / 0.35) : top + (toZ[m] - top) * smooth((h - 0.65) / 0.35);
  fx[m] = fromX[m] + (toX[m] - fromX[m]) * smooth((h - 0.3) / 0.4);
}

void planSwing(int m, float landX) {
  if (fabs(landX - edgeX) < 25) landX = edgeX + 25;   // never on the edge itself: a little further, up on the step
  fromX[m] = fx[m]; fromZ[m] = fz[m];
  toX[m] = landX; toZ[m] = groundAt(landX);
}

float neutralX(int m) { return MOUNT[m][0] + CLIMB_REACH * cos(radians(MOUNT[m][2])); }

// parts: 0 weight back, 1 both front feet up, over and down onto the step, 2 pull the body forward,
// 3 the wave: one leg at a time while the body creeps forward, until every foot is up (the first round only catches
// the legs up after the pull, the last one puts every foot back under its hip), 4 done
void stepTick(float dt) {
  if (!stepGo) dt = 0;
  partT += dt;
  float back = 0;
  if (part == 0) {
    back = smooth(partT / 1.5);
    if (partT >= 1.5) { part = 1; partT = 0; planSwing(0, edgeX + ON_STEP); planSwing(3, edgeX + ON_STEP); }
  } else if (part == 1) {
    back = 1;
    float h = partT / (2 * SWING_S);
    swingFoot(0, h); swingFoot(3, h);
    if (h >= 1) { gnd[0] = toZ[0]; gnd[3] = toZ[3]; part = 2; partT = 0; }
  } else if (part == 2) {
    float k = smooth(partT / 3.0);
    back = 1 - k;
    bodyX = PULL * k;
    if (partT >= 3.0) { part = 3; partT = 0; roundX = bodyX; swingIdx = 0; }
  } else if (part == 3) {
    int m = WAVE[swingIdx];
    bool still = lastRound || rounds == 0;   // body holds still this round
    // land 5/12 of a stride ahead of where the hip will be at touchdown, so each foot passes under its hip mid-stance
    float bodyAtLanding = still ? roundX : roundX + STEP_STRIDE * (swingIdx + 1) / 6;
    if (!planned) planSwing(m, bodyAtLanding + neutralX(m) + (lastRound ? 0 : STEP_STRIDE * 5 / 12));
    planned = true;
    float h = min(partT / SWING_S, 1.0f);
    swingFoot(m, h);
    if (!still) bodyX = roundX + STEP_STRIDE * (swingIdx + h) / 6;
    if (h >= 1) {
      gnd[m] = toZ[m]; partT = 0; planned = false;
      if (++swingIdx == 6) {
        swingIdx = 0; rounds++; roundX = bodyX;
        bool allUp = true;
        for (int i = 0; i < 6; i++) if (gnd[i] < stepH) allUp = false;
        if (lastRound) part = 4;
        // the last round puts every foot back under its hip, so the back feet's hip spot must be past the edge too
        else if ((allUp && roundX + neutralX(2) > edgeX + 25) || rounds >= 10) lastRound = true;
      }
    }
  }
  // body height follows the feet; nose tilts up while the front is higher than the back
  float front = (gnd[0] + gnd[3]) / 2, middle = (gnd[1] + gnd[4]) / 2, rear = (gnd[2] + gnd[5]) / 2;
  bodyZ += constrain((front + middle + rear) / 3 - bodyZ, -1.0f, 1.0f);
  float wantTilt = STEP_TILT * degrees(atan2(front - rear, neutralX(0) - neutralX(2)));
  tilt += constrain(wantTilt - tilt, -0.3f, 0.3f);

  // eases from the climb-mode pose into the climbing pose over the first second, and back over the last
  float into = smooth(stepT / 1.0) * (part == 4 ? 1 - smooth((partT) / 1.5) : 1);
  stepT += dt;
  bX = bodyX - HOLD_BACK * back; bY = 0; bZ = bodyZ; bRoll = 0; bYaw = 0;
  bPitch = -(CLIMB_PITCH + into * (STEP_LEAN - CLIMB_PITCH)) - tilt;
  float base = STAND_Z - (max(height, CLIMB_HEIGHT) + into * (STEP_RIDE - max(height, CLIMB_HEIGHT)));
  for (int m = 0; m < 6; m++) {
    int leg = legAt(m);
    float a[3];
    if (!placeFoot(leg, fx[m], fy[m], base + fz[m], a)) continue;
    for (int j = 0; j < 3; j++) {
      a[j] = constrain(a[j], climbPrev[m][j] - CLIMB_SLEW, climbPrev[m][j] + CLIMB_SLEW);
      climbPrev[m][j] = a[j];
      writeJoint(leg, j, a[j]);
    }
  }
  if (part == 4 && fabs(bodyZ - stepH) < 0.5 && fabs(tilt) < 0.2 && partT >= 1.5) {
    mode = 'w'; moving = false; amp = 0; stepGo = false;   // now standing on the step, which is the new floor
    Serial.println("on the step");
    rumble(300);
  }
}

// ---------- controller ----------
bool last[12];
uint8_t lastDpad = 0;

void onConnectedController(ControllerPtr ctl) {
  if (!pad) { pad = ctl; Serial.println("controller connected"); rumble(200); }
}

void onDisconnectedController(ControllerPtr ctl) {
  if (ctl == pad) { pad = nullptr; moving = false; Serial.println("controller lost: stopping"); }
}

float stick(int32_t v) {
  if (abs(v) < 120) return 0;   // worn sticks rest off-centre after use; a small deadzone let that creep the legs
  return constrain(v / 512.0f, -1.0f, 1.0f);
}

bool pressed(int i, bool now) { bool p = now && !last[i]; last[i] = now; return p; }

void readPad() {
  if (!pad || !pad->isConnected() || !pad->hasData()) return;
  if (pressed(0, pad->throttle() > 500)) standUp();
  if (pressed(1, pad->brake() > 500)) sitDown(true);
  if (pressed(2, pad->miscStart())) off();
  if (pressed(3, pad->a())) { if (pad->l1()) toggleClimb(); else if (climb) startStep(); else startAnim('v'); }
  if (pressed(4, pad->b())) startAnim('g');
  if (pressed(5, pad->x())) startAnim('o');
  if (pressed(6, pad->y())) startAnim('q');
  if (pressed(7, pad->thumbR())) toggleBrain();
  if (pressed(8, pad->thumbL())) toggleLearned();
  if (pressed(9, pad->miscBack())) cycleLegOut();
  if (mode == 'a' && (fabs(stick(pad->axisY())) > 0.5 || fabs(stick(pad->axisX())) > 0.5)) cancelAnim(0);
  uint8_t dp = pad->dpad();
  if ((dp & DPAD_UP) && !(lastDpad & DPAD_UP)) { if (climb) changeStep(10); else changeHeight(5); }
  if ((dp & DPAD_DOWN) && !(lastDpad & DPAD_DOWN)) { if (climb) changeStep(-10); else changeHeight(-5); }
  if ((dp & DPAD_RIGHT) && !(lastDpad & DPAD_RIGHT)) changeSpeed(-50);
  if ((dp & DPAD_LEFT) && !(lastDpad & DPAD_LEFT)) changeSpeed(50);
  lastDpad = dp;

  leanTR = leanTP = 0;
  if (mode == 'c') stepGo = -stick(pad->axisY()) > 0.3;
  if (mode != 'w' || anim || pending) return;
  float k = pad->r1() ? 0.4 : 1.0;
  float f = -stick(pad->axisY()) * k, sd = -stick(pad->axisX()) * k, r = -stick(pad->axisRX()) * k;
  if (pad->l1()) {
    leanTR = stick(pad->axisRX()) * 8;
    leanTP = -stick(pad->axisRY()) * 8;
    r = 0;
  }
  if (learned || legOut >= 0) sd = r = 0;
  if (climb) sd = 0;
  if (settling) f = sd = r = 0;
  if (f != 0 || sd != 0 || r != 0) { fwd = f; side = sd; turn = r; moving = true; }
  else moving = false;
}

void setup() {
  Serial.begin(115200);
  Wire.begin(8, 9);
  Wire1.begin(4, 5);
  for (auto *p : {&pca1, &pca2}) {
    p->begin();
    p->setOscillatorFrequency(27000000);
    p->setPWMFreq(50);
  }
  delay(10);
  ik(0, MOUNT[0][0] + REACH * cos(radians(MOUNT[0][2])), MOUNT[0][1] + REACH * sin(radians(MOUNT[0][2])), STAND_Z, STAND_DEG);
  allOff();
  BP32.setup(&onConnectedController, &onDisconnectedController);
  Serial.printf("VANTA ready (channel map 2026-11-24), servos OFF, mirror %s. R2 stand, L2 sit+off, A wave, B dance, X bow, Y rear up, View injured leg\n", mirror ? "ON" : "off");
}

void serialCommand(char c) {
  if (c >= '1' && c <= '6') { selLeg = c - '1'; selJoint = -1; showSel(); }
  else if (c == 'c' || c == 'f' || c == 't') {
    selJoint = c == 'c' ? 0 : c == 'f' ? 1 : 2;
    mode = 'j'; writeJoint(selLeg, selJoint, STAND_DEG[selJoint]); showSel();
  } else if (selJoint >= 0 && (c == '+' || c == '-' || c == ']' || c == '[')) {
    int step = (c == '+' || c == '-') ? 10 : 50;
    HOME_US[selLeg][selJoint] = constrain(HOME_US[selLeg][selJoint] + (c == '+' || c == ']' ? step : -step), 600, 2400);
    writeJoint(selLeg, selJoint, STAND_DEG[selJoint]); showSel();
  } else if (selJoint >= 0 && c == 'n') {
    SIGN[selLeg][selJoint] = -SIGN[selLeg][selJoint]; showSel();
  } else if (selJoint >= 0 && c == 'e') {
    Serial.println(selJoint == 0 ? "+15: leg should swing counterclockwise seen from above" :
                   selJoint == 1 ? "+15: knee should LIFT" : "+15: foot should swing IN toward the body");
    for (int d = 0; d <= 15; d++) { writeJoint(selLeg, selJoint, STAND_DEG[selJoint] + d); delay(30); }
    delay(600);
    for (int d = 15; d >= 0; d--) { writeJoint(selLeg, selJoint, STAND_DEG[selJoint] + d); delay(30); }
  } else if (c == 'p') printArrays();
  else if (c == 'u') standUp();
  else if (c == 'd') sitDown(false);
  else if (c == 'w' || c == 'b' || c == 'l' || c == 'r') {
    if (mode != 'w' || anim || pending) { Serial.println("stand up first: u"); return; }
    fwd = c == 'w' ? 1 : c == 'b' ? -1 : 0;
    turn = c == 'l' ? 1 : c == 'r' ? -1 : 0;
    side = 0;
    moving = true;
  } else if (c == ' ') { moving = false; stepGo = false; cancelAnim(0); }
  else if (c == 'a') { if (mode == 'c') stepGo = true; else { startStep(); stepGo = mode == 'c'; } }
  else if (c == 'x') off();
  else if (c == 'v' || c == 'g' || c == 'o' || c == 'q') startAnim(c);
  else if (c == 'k') toggleBrain();
  else if (c == 'y') toggleLearned();
  else if (c == 'i') cycleLegOut();
  else if (c == 'h') toggleClimb();
  else if (c == 'm') { mirror = !mirror; Serial.printf("mirror %s\n", mirror ? "ON" : "off"); }
  else if (c == '9' || c == '0') { stride = constrain(stride + (c == '0' ? 10 : -10), 10.0f, 140.0f); Serial.printf("stride %.0f mm\n", stride); }
  else if (c == '7' || c == '8') { lift = constrain(lift + (c == '8' ? 5 : -5), 10.0f, 100.0f); Serial.printf("lift %.0f mm\n", lift); }
  else if (c == '=' || c == '_') changeSpeed(c == '=' ? -50 : 50);
  else if (c == '>') changeHeight(5);
  else if (c == '<') changeHeight(-5);
  else if (c == 'z') { BP32.forgetBluetoothKeys(); Serial.println("forgot paired controllers"); }
}

void loop() {
  if (BP32.update()) readPad();
  if (Serial.available()) serialCommand(Serial.read());

  static unsigned long lastMs = millis();
  unsigned long now = millis();
  float dt = now - t0;
  // further stick = shorter step time, so the legs speed up as well as stepping longer
  float push = moving ? max(max(fabs(fwd), fabs(side)), fabs(turn)) : 0;
  if (mode != 'w' && mode != 'c') climb = false;
  climbK = constrain(climbK + (climb ? 0.02f : -0.02f), 0.0f, 1.0f);
  if (climbK > 0 && climbK < 1) moving = false;   // no walking while the body shifts between poses
  float slowC = climbK > 0 ? CLIMB_SLOW : SLOW_CYCLE, fastC = climbK > 0 ? CLIMB_CYCLE : cycle;
  float step = (now - lastMs) / (slowC + (fastC - slowC) * push);
  phase = fmod(phase + step, 1.0f);
  gaitPh = fmod(gaitPh + (fwd < 0 ? -step : step), 1.0f);
  lastMs = now;
  float base = STAND_Z - (height + climbK * (max(height, CLIMB_HEIGHT) - height));

  if (mode == 'u') {
    // first pull the feet in at sitting height, then push the body up
    float tuck = min(1.0f, dt / TUCK_MS), rise = constrain((dt - TUCK_MS) / RISE_MS, 0.0f, 1.0f);
    float r = SIT_REACH + (REACH - SIT_REACH) * tuck, z = SIT_Z + (base - SIT_Z) * rise;
    for (int leg = 0; leg < 6; leg++) footAt(leg, r, z);
    if (rise >= 1) { mode = 'w'; moving = false; amp = 0; Serial.println("standing"); rumble(150); }
  } else if (mode == 'd') {
    float lower = min(1.0f, dt / RISE_MS), spread = constrain((dt - RISE_MS) / TUCK_MS, 0.0f, 1.0f);
    float r = REACH + (SIT_REACH - REACH) * spread, z = base + (SIT_Z - base) * lower;
    for (int leg = 0; leg < 6; leg++) footAt(leg, r, z);
    if (spread >= 1) {
      mode = 'i'; Serial.println("sitting");
      if (offAfterSit) off();
    }
  } else if (mode == 'w') {
    amp = moving ? min(1.0f, amp + 20 / RAMP_MS) : max(0.0f, amp - 20 / RAMP_MS);
    if (pending && amp == 0) {
      anim = pending; pending = 0; animT0 = now; mode = 'a';
      Serial.println(anim == 'v' ? "wave" : anim == 'g' ? "dance" : anim == 'o' ? "bow" : "rear up");
      rumble(120);
    } else {
      leanR += (leanTR - leanR) * 0.15;
      leanP += (leanTP - leanP) * 0.15;
      bX = bY = bZ = bYaw = 0; bRoll = leanR; bPitch = leanP;
      settling = false;
      for (int m = 0; m < 6; m++) if (tuck[m] != (m == legOut ? 1 : 0)) settling = true;
      if (sitQueued && !settling && climbK == 0) { sitQueued = false; sitDown(offAfterSit); }
      bool net = learned || legOut >= 0 || settling;
      float off[6][3];
      if (net) netWalk(legOut >= 0 ? WALK_NO_RL : WALK6, gaitPh, off);
      for (int m = 0; net && m < 6; m++) {
        int leg = legAt(m);
        float x, y, a[3];
        neutral(leg, REACH, x, y);
        if (!placeFoot(leg, x, y, base, a)) continue;
        tuck[m] = constrain(tuck[m] + (m == legOut ? 0.02f : -0.02f), 0.0f, 1.0f);
        // rear-right out is the rear-left walk mirrored: swap sides, flip the coxas
        int src = legOut == 5 ? (m + 3) % 6 : m;
        float k = amp * (1 - tuck[m]), t = smooth(tuck[m]);
        a[0] += k * off[src][0] * (legOut == 5 ? -1 : 1);
        a[1] += k * off[src][1] + t * (70 - a[1]);
        a[2] += k * off[src][2] + t * (60 - a[2]);
        // the network likes to snap joints across; hold it to what an MG995 can follow (the sim's servos
        // were limited the same way) so 18 servos never all get a big step at once
        for (int j = 0; j < 3; j++) {
          a[j] = netOn ? constrain(a[j], netPrev[m][j] - NET_SLEW, netPrev[m][j] + NET_SLEW) : a[j];
          netPrev[m][j] = a[j];
          writeJoint(leg, j, a[j]);
        }
      }
      netOn = net;
      bool climbing = !net && climbK > 0;
      if (climbing) { bX = -CLIMB_BACK * climbK; bPitch = leanP - CLIMB_PITCH * climbK; }
      float reach = REACH + climbK * (CLIMB_REACH - REACH);
      for (int leg = 0; climbing && leg < 6; leg++) {
        int m = mnt(leg);
        float x, y, a[3];
        neutral(leg, reach, x, y);
        float n = hypot(x, y), g = radians(MOUNT[m][2]);
        // back legs first, then middle, then front, right side then left
        float p = fmod(phase - (5 - m) / 6.0f + 1, 1.0f), s, up = 0, out = 0;
        if (p < CLIMB_DUTY) s = 0.5 - p / CLIMB_DUTY;
        else {
          float h = (p - CLIMB_DUTY) / (1 - CLIMB_DUTY);
          // straight up, over, straight down: an arc moves forward while rising and catches the toe on the step edge
          up = min(smooth(h / 0.35), 1 - smooth((h - 0.65) / 0.35));
          s = -0.5 + smooth((h - 0.3) / 0.4);
          out = sin(PI * h);   // reaching out a little at the top lets the foot go higher
        }
        float fx = x + ((fwd * CLIMB_STRIDE + turn * TURN_MM * (-y / n)) * s + CLIMB_OUT * out * cos(g)) * amp;
        float fy = y + (turn * TURN_MM * (x / n) * s + CLIMB_OUT * out * sin(g)) * amp;
        float z = base + CLIMB_LIFT * up * amp;
        while (!(placeFoot(leg, fx, fy, z, a) && fits(a)) && z > base) z = max(base, z - 5);
        if (!placeFoot(leg, fx, fy, z, a)) continue;
        for (int j = 0; j < 3; j++) {
          if (climbOn) a[j] = constrain(a[j], climbPrev[m][j] - CLIMB_SLEW, climbPrev[m][j] + CLIMB_SLEW);
          climbPrev[m][j] = a[j];
          writeJoint(leg, j, a[j]);
        }
      }
      climbOn = climbing;
      for (int leg = 0; !net && !climbing && leg < 6; leg++) {
        float x, y;
        neutral(leg, REACH, x, y);
        float n = hypot(x, y);
        float p = fmod(phase + PHASE[leg], 1.0f), s, z = base;
        if (p < 0.5) s = 0.5 - p * 2;
        else {
          float h = p * 2 - 1, sn = sin(PI * h);
          s = -0.5 + h * h * (3 - 2 * h);
          z += lift * sn * sn;   // sin squared: the foot is moving at zero speed when it touches down, plain sin slams it
        }
        float dx = fwd * stride + turn * TURN_MM * (-y / n);
        float dy = side * stride + turn * TURN_MM * (x / n);
        placeFoot(leg, x + dx * s * amp, y + dy * s * amp, base + (z - base) * amp);
      }
    }
  }

  if (mode == 'c') stepTick(0.02);

  if (mode == 'a') {
    float t = cancelT0 ? cancelAt : (now - animT0) / 1000.0;
    float k = cancelT0 ? 1 - smooth((now - cancelT0) / CANCEL_MS) : 1;
    resetPose();
    int skip = -1;
    float wa[3];
    if (anim == 'v') wave(t, skip, wa);
    else if (anim == 'g') dance(t);
    else if (anim == 'o') bow(t);
    else rearUp(t);
    bX *= k; bY *= k; bZ *= k; bRoll *= k; bPitch *= k; bYaw *= k;
    for (int leg = 0; leg < 6; leg++) {
      float x, y, sa[3];
      neutral(leg, REACH, x, y);
      if (leg == skip) {
        if (!placeFoot(leg, x, y, base, sa)) continue;
        for (int j = 0; j < 3; j++) writeJoint(leg, j, sa[j] + k * (wa[j] - sa[j]));
        continue;
      }
      placeFoot(leg, x + k * oX[leg], y + k * oY[leg], base + k * oZ[leg]);
    }
    if (t >= animLength(anim) || k <= 0) { anim = 0; cancelT0 = 0; resetPose(); mode = 'w'; Serial.println("standing"); }
  }
  delay(20);
}
