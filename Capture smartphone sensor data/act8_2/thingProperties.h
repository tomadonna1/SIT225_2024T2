// Code generated by Arduino IoT Cloud, DO NOT EDIT.

#include <ArduinoIoTCloud.h>
#include <Arduino_ConnectionHandler.h>

// thingProperties.h
#include "arduino_secrets.h"

const char SSID[]     = SECRET_SSID;    // Network SSID (name)
const char PASS[]     = SECRET_OPTIONAL_PASS;    // Network password (use for WPA, or use as key for WEP)

// Additional LIBRARY: ArduinoHttpClient
#include "arduino_secrets.h"

void on_X_changed();
void on_Y_changed();
void on_Z_changed();

float accelerometer_X;
float accelerometer_Y;
float accelerometer_Z;

void initProperties(){
  ArduinoCloud.addProperty(accelerometer_X, READWRITE, ON_CHANGE, on_X_changed);
  ArduinoCloud.addProperty(accelerometer_Y, READWRITE, ON_CHANGE, on_Y_changed);
  ArduinoCloud.addProperty(accelerometer_Z, READWRITE, ON_CHANGE, on_Z_changed);

}

WiFiConnectionHandler ArduinoIoTPreferredConnection(SSID, PASS);
