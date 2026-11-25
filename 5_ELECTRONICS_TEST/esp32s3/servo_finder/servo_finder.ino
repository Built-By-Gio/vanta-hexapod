// Finds which driver/channel each servo is on. Serial Monitor 115200, "No line ending".
// Type "<driver> <channel>" to jump straight to one, e.g. "2 6" wiggles driver 2 ch 6.
// Add a pulse to hold it there instead: "2 6 1700" (500-2500 us) until x.
// n = next channel, b = previous, r = wiggle again, x = all off.
// Each step wiggles one channel a little (1500 -> 1600 -> 1400 -> 1500) and then turns it off.
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca1(0x40, Wire);
Adafruit_PWMServoDriver pca2(0x40, Wire1);

int pos = -1;   // 0-15 = driver 1 ch 0-15, 16-31 = driver 2 ch 0-15

void allOff() {
  for (int ch = 0; ch < 16; ch++) { pca1.setPWM(ch, 0, 4096); pca2.setPWM(ch, 0, 4096); }
}

void wiggle(int p) {
  Adafruit_PWMServoDriver &d = p < 16 ? pca1 : pca2;
  int ch = p % 16;
  Serial.printf("DRIVER %d  ch %d  (GPIO %s)\n", p < 16 ? 1 : 2, ch, p < 16 ? "8/9" : "4/5");
  for (int us : {1500, 1600, 1400, 1500}) { d.writeMicroseconds(ch, us); delay(400); }
  d.setPWM(ch, 0, 4096);
}

bool found(TwoWire &w) {
  w.beginTransmission(0x40);
  return w.endTransmission() == 0;
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);
  Wire.begin(8, 9);
  Wire1.begin(4, 5);
  for (auto *p : {&pca1, &pca2}) {
    p->begin();
    p->setOscillatorFrequency(27000000);
    p->setPWMFreq(50);
  }
  delay(10);
  allOff();
  delay(500);
  Serial.printf("driver 1 (GPIO 8/9): %s\n", found(Wire) ? "found" : "NOT FOUND, check its 4 wires");
  Serial.printf("driver 2 (GPIO 4/5): %s\n", found(Wire1) ? "found" : "NOT FOUND, check its 4 wires");
  Serial.println("\"2 6\" = wiggle driver 2 ch 6, \"2 6 1700\" = hold it at 1700us, n/b = next/back, r = repeat, x = all off");
}

void loop() {
  if (!Serial.available()) return;
  String in = Serial.readString();
  in.trim();
  int drv, ch, us;
  int got = sscanf(in.c_str(), "%d %d %d", &drv, &ch, &us);
  if (got >= 2) {
    if ((drv != 1 && drv != 2) || ch < 0 || ch > 15) { Serial.println("driver 1 or 2, channel 0-15"); return; }
    pos = (drv - 1) * 16 + ch;
    if (got == 3) {
      us = constrain(us, 500, 2500);
      (drv == 1 ? pca1 : pca2).writeMicroseconds(ch, us);
      Serial.printf("DRIVER %d  ch %d  holding %d us (x to release)\n", drv, ch, us);
    } else wiggle(pos);
    return;
  }
  char c = in.length() ? in[0] : 0;
  if (c == 'n') { pos = (pos + 1) % 32; wiggle(pos); }
  else if (c == 'b') { pos = (pos + 31) % 32; wiggle(pos); }
  else if (c == 'r' && pos >= 0) wiggle(pos);
  else if (c == 'x') { allOff(); Serial.println("off"); }
}
