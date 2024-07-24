#include "arduino_secrets.h"
#include "thingProperties.h"

const int trigger = 8;
const int echo = 9;

int getUltrasonicDistance(){
  // Function to retreive the distance reading of the ultrasonic sensor
  long duration;

  // Assure the trigger pin is LOW:
  digitalWrite(trigger, LOW);
  // Brief pause:
  delayMicroseconds(5);

  // Trigger the sensor by setting the trigger to HIGH:
  digitalWrite(trigger, HIGH);
  // Wait a moment before turning off the trigger:
  delayMicroseconds(10);
  // Turn off the trigger:
  digitalWrite(trigger, LOW);

  // Read the echo pin:
  duration = pulseIn(echo, HIGH);
  // Calculate the distance in centimeter (CM):
  distance = duration * 0.034 / 2;

  // Return the distance read from the sensor:
  return distance;
}

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

  // Define inputs and outputs:
  pinMode(trigger, OUTPUT);
  pinMode(echo, INPUT);
}

void loop() {
  ArduinoCloud.update();
  // Your code here 
  
  // Print the distance to the serial monitor:
  Serial.print("Distance: ");
  Serial.println(getUltrasonicDistance());

  // Wait one second before continuing:
  delay(1000);
}

/*
  Since distance is READ_WRITE variable, onDistanceChange() is
  executed every time a new value is received from IoT Cloud.
*/
void onDistanceChange(){
  Serial.print("--onDistanceChange");
}

