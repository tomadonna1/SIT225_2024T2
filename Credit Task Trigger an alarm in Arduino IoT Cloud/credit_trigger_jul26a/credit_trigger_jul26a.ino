#include "arduino_secrets.h"
#include "thingProperties.h"
#include <Arduino_LSM6DS3.h>

void setup() {
  // Initialize serial and wait for port to open:
  Serial.begin(9600);
  // This delay gives the chance to wait for a Serial Monitor without blocking if none is found
  delay(1500); 

  // Defined in thingProperties.h
  initProperties();

  // Connect to Arduino IoT Cloud
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);
  
  /*
     The following function allows you to obtain more information
     related to the state of network and IoT Cloud connection and errors
     the higher number the more granular information you’ll get.
     The default is 0 (only errors).
     Maximum is 4
 */
  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();

  if (!IMU.begin()) {
//    Serial.println("Failed to initialize IMU!");
    while (1);
  }

}

void loop() {
  ArduinoCloud.update();
  // Your code here 
  // read accelero data
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
  }

  // Default severe warning
  severe_level = false;

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
    severe_level = true; // boolean to send warning to email
  }

  Serial.println(String(rollF) + ", " + String(pitchF) + ", " + String(level));
}



/*
  Since PitchF is READ_WRITE variable, onPitchFChange() is
  executed every time a new value is received from IoT Cloud.
*/
void onPitchFChange()  {
  Serial.print("--onPitchFChange");
}

/*
  Since RollF is READ_WRITE variable, onRollFChange() is
  executed every time a new value is received from IoT Cloud.
*/
void onRollFChange()  {
  Serial.print("--onRollFChange");
}

/*
  Since Level is READ_WRITE variable, onLevelChange() is
  executed every time a new value is received from IoT Cloud.
*/
void onLevelChange()  {
  Serial.print("--onLevelChange");
}

/*
  Since SevereLevel is READ_WRITE variable, onSevereLevelChange() is
  executed every time a new value is received from IoT Cloud.
*/
void onSevereLevelChange()  {
  Serial.print("--onSevereLevelChange");
}