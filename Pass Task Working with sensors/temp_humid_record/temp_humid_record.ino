#include <DHT.h>

#define DHTPIN 10  // digital pin number
#define DHTTYPE DHT22  // DHT type 11 or 22
DHT dht(DHTPIN, DHTTYPE);

// variables to store data.
float hum, temp;

void setup() {
  // Set baud rate for serial communication
  Serial.begin(9600);

  // initialise DHT libarary
  dht.begin();
}

void loop() {
  // read data
  hum = dht.readHumidity();
  temp = dht.readTemperature();

  // Print data to serial port - a compact way
  Serial.println(String(hum) + "," + String(temp));
  
  // wait 2 seconds before updating the data
  delay(2000);
}
