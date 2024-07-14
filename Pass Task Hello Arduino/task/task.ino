int x;

void setup() {
  Serial.begin(9600);  // set baud rate
  pinMode(LED_BUILTIN, OUTPUT); // set up built in led as output
}

void loop() {
  while (!Serial.available()) {} // wait for data to arrive

  // read string data from Python and blink for that number of times at 1 second interval
  x = Serial.readString().toInt();
  for(int i = 0; i < x; i++){
      digitalWrite(LED_BUILTIN, HIGH);
      delay(1000);
      digitalWrite(LED_BUILTIN, LOW);
      delay(1000);
    }

// Generate random number between 1 and 6
  int ArduinoRandom = random(1,6);
  Serial.println(ArduinoRandom);

//  small delay to ensure data is sent propery
  delay(50);

  // Push the data through serial channel.
  Serial.flush();  
}
