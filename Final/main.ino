#include <IBusBM.h>

IBusBM ibus;

// Channel Values
int rcCH1 = 0;
int rcCH2 = 0;
int rcCH3 = 0;
int rcCH5 = 0;
bool rcCH6 = 0;

// LED
#define carLED 13

// Motor A
#define pwmA 4
#define dirA 3

// Motor B
#define pwmB 7
#define dirB 5

// Motor Speed & Direction
int MotorSpeedA = 0;
int MotorSpeedB = 0;

// Direction: 0 = backward, 1 = forward
int MotorDirA = 1;
int MotorDirB = 1;

// -------- Motor Control Functions --------
void mControlA(int mspeed, int mdir) {
  digitalWrite(dirA, mdir);      // SINGLE direction pin
  analogWrite(pwmA, mspeed);
}

void mControlB(int mspeed, int mdir) {
  digitalWrite(dirB, mdir);      // SINGLE direction pin
  analogWrite(pwmB, mspeed);
}

// -------- Channel Read Functions --------
int readChannel(byte channelInput, int minLimit, int maxLimit, int defaultValue) {
  uint16_t ch = ibus.readChannel(channelInput);
  if (ch < 100) return defaultValue;
  return map(ch, 1000, 2000, minLimit, maxLimit);
}

bool readSwitch(byte channelInput, bool defaultValue) {
  int intDefaultValue = (defaultValue) ? 100 : 0;
  int ch = readChannel(channelInput, 0, 100, intDefaultValue);
  return (ch > 50);
}

void setup() {
  Serial.begin(115200);
  ibus.begin(Serial1);

  pinMode(pwmA, OUTPUT);
  pinMode(dirA, OUTPUT);
  pinMode(pwmB, OUTPUT);
  pinMode(dirB, OUTPUT);

  pinMode(carLED, OUTPUT);
}

void loop() {

  rcCH1 = readChannel(0, -100, 100, 0);
  rcCH2 = readChannel(1, -100, 100, 0);
  rcCH3 = readChannel(2, 0, 155, 0);
  rcCH5 = readChannel(4, -100, 100, 0);
  rcCH6 = readSwitch(5, false);

  // Base speed
  MotorSpeedA = rcCH3;
  MotorSpeedB = rcCH3;

  if (rcCH6) {
    // ===== SPIN MODE =====
    digitalWrite(carLED, HIGH);

    if (rcCH5 >= 0) {
      MotorDirA = 0;
      MotorDirB = 1;
    } else {
      MotorDirA = 1;
      MotorDirB = 0;
    }

    MotorSpeedA += abs(rcCH5);
    MotorSpeedB += abs(rcCH5);

  } else {
    // ===== NORMAL MODE =====
    digitalWrite(carLED, LOW);

    if (rcCH2 >= 0) {
      MotorDirA = 1;
      MotorDirB = 1;
    } else {
      MotorDirA = 0;
      MotorDirB = 0;
    }

    MotorSpeedA += abs(rcCH2);
    MotorSpeedB += abs(rcCH2);

    MotorSpeedA -= rcCH1;
    MotorSpeedB += rcCH1;
  }

  MotorSpeedA = constrain(MotorSpeedA, 0, 255);
  MotorSpeedB = constrain(MotorSpeedB, 0, 255);

  mControlA(MotorSpeedA, MotorDirA);
  mControlB(MotorSpeedB, MotorDirB);

  delay(50);
}