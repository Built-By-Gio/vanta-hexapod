// Serial servo console for the PCA9685. 115200 baud, one command per line:
//   S <ch> <us>   set channel 0-15 to a pulse in microseconds (500-2500)
//   O <ch>        channel off (servo goes limp)
//   X             all channels off
// Every channel starts off, so nothing moves until the page sends something.
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// ESP32-S3 DevKitC: PCA9685 SDA -> GPIO 8, SCL -> GPIO 9, VCC -> 3V3
const int SDA_PIN = 8, SCL_PIN = 9;

Adafruit_PWMServoDriver pwm(0x40);
char line[24];
uint8_t len = 0;

void allOff() {
  for (int ch = 0; ch < 16; ch++) pwm.setPWM(ch, 0, 4096);
}

void run(char *s) {
  int ch, us;
  if (s[0] == 'S' && sscanf(s + 1, "%d %d", &ch, &us) == 2 && ch >= 0 && ch < 16) {
    us = constrain(us, 500, 2500);
    pwm.writeMicroseconds(ch, us);
    Serial.print("ok S "); Serial.print(ch); Serial.print(' '); Serial.println(us);
  } else if (s[0] == 'O' && sscanf(s + 1, "%d", &ch) == 1 && ch >= 0 && ch < 16) {
    pwm.setPWM(ch, 0, 4096);
    Serial.print("ok O "); Serial.println(ch);
  } else if (s[0] == 'X') {
    allOff();
    Serial.println("ok X");
  } else {
    Serial.print("? "); Serial.println(s);
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(50);
  delay(10);
  allOff();
  Serial.println("ready");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (len) { line[len] = 0; run(line); len = 0; }
    } else if (len < sizeof(line) - 1) {
      line[len++] = c;
    }
  }
}
