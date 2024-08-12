#include <Arduino_LSM6DS3.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <WiFiNINA.h>
#include <ArduinoJson.h>

// WiFi Credentials
char ssid[] = "Long's hotspot";
char pass[] = "123456677";

int status = WL_IDLE_STATUS;

// Initialize WiFi client
WiFiSSLClient wifi_client; 

// Connect to Wifi Access Point
void connectToAP(){
  while (status != WL_CONNECTED){
      Serial.print("Attempting to connect to SSID: ");
      Serial.println(ssid);

      // Connect to WPA/WP2 network
      status = WiFi.begin(ssid, pass);

      // wait 5 second for connection
      delay(5000);

      if (status == WL_CONNECTED){
          Serial.println("Connected to WiFi");
          printWifiStatus();
        }else{
            Serial.println("Failed to connect. Retrying...");
          }
      Serial.println("Connected");
    }
  }

// Print results to serial monitor
void printWifiStatus(){ 
  // Network SSID
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // Device IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  }

// Gyroscope axis
float x, y, z;


/******* MQTT Broker Connection Details *******/
const char* mqtt_server = "943103f9e51648f9b2e42b0741f78511.s1.eu.hivemq.cloud";
const char* mqtt_username = "tomadonna";
const char* mqtt_password = "L@ongonly1";
const int mqtt_port =8883;

/**** MQTT Client Initialisation Using WiFi Connection *****/
PubSubClient client(wifi_client);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];


/************* Connect to MQTT Broker ***********/
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "LongID";   // Create a random client ID
    //clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");

     //
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");   // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}


/***** Call back Method for Receiving MQTT messages ****/

void callback(char* topic, byte* payload, unsigned int length) {
  String incommingMessage = "";
  for (int i = 0; i < length; i++) incommingMessage+=(char)payload[i];

  Serial.println("Message arrived ["+String(topic)+"]"+incommingMessage);

  //--- check the incomming message
    if( strcmp(topic,"led_state") == 0){
     //
  }

}


/**** Method for Publishing MQTT Messages **********/
void publishMessage(const char* topic, String payload , boolean retained){
  if (client.publish(topic, payload.c_str(), true)){
      Serial.println("Message publised ["+String(topic)+"]: "+payload);
    } else{
        Serial.println("Message publish failed");
      }
}


void setup() {
  Serial.begin(9600); // set baud rate
  while (!Serial);  // wait for port to init

  if (!IMU.begin()) {
    while (1);
  }

  // Check for the WiFi module
  if (WiFi.status() == WL_NO_MODULE){
      Serial.println("WiFi module failed!");
      while (true);
    }

  // wifi connection
  connectToAP();
  printWifiStatus();


  //mqtt connection
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  // check if client is connected
  if (!client.connected()) reconnect(); // check if client is connected
  client.loop();
  
  // read accelero data
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
  }

  Serial.println(String(x) + "," + String(y) + "," + String(z));

  DynamicJsonDocument doc(1024);
  doc["x"] = x;
  doc["y"] = y;
  doc["z"] = z;

  char mqtt_message[128];
  serializeJson(doc, mqtt_message);

  publishMessage("data", mqtt_message, true); // send topic and data 
  
  
  delay(5000); // delay 5s
}
