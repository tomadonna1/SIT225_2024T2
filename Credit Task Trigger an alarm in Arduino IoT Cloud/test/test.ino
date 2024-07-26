#include <Arduino_LSM6DS3.h>

float x, y, z;
float level,roll,pitch,rollF,pitchF=0;

void setup() {
  Serial.begin(9600); // set baud rate
  while (!Serial);  // wait for port to init
//  Serial.println("Started");

  if (!IMU.begin()) {
//    Serial.println("Failed to initialize IMU!");
    while (1);
  }

//  Serial.println(
//    "Accelerometer sample rate = " 
//    + String(IMU.accelerationSampleRate()) + " Hz");
}

void loop() {
  // read accelero data
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
  }

 // Calculation of roll and pitch (rotation around X-axis, rotation around Y-axis)
 roll = atan(y/sqrt(pow(x,2) + pow(z,2))) * 180/PI;
 pitch = atan(-1 * x/sqrt(pow(y,2) + pow(z,2))) * 180/PI;

 // Low-pass filter
 rollF = 0.94 * rollF + 0.06 * roll;
 pitchF = 0.94 * pitchF + 0.06 * pitch;
 
// Determine the level of eathquake based on rollF and pitchF
 if (abs(rollF) < 3 && abs(pitchF) < 3) {
    level = 1;
  }
 else if ((abs(rollF) >= 3 && abs(rollF) < 6) || (abs(pitchF) >= 3 && abs(pitchF) < 6)){
    level = 2;
    Serial.println(String(rollF) + ", " + String(pitchF) + ", " + level);
  }
 else if ((abs(rollF) >= 6 && abs(rollF) < 9) || (abs(pitchF) >= 6 && abs(pitchF) < 9)){
    level = 3;
    Serial.println(String(rollF) + ", " + String(pitchF) + ", " + level);
  }
 else if (abs(rollF) >= 9 || abs(pitchF) >= 9){
    level = 4;
  }

  Serial.println(String(rollF) + ", " + String(pitchF) + ", " + String(level));

 

 
//  Serial.print(rollF);
//  Serial.print('/');
//  Serial.println(pitchF);
  
  delay(100);
}
