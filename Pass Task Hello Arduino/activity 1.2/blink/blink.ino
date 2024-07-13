/*
    Ahsan Habib (habib@deakin.edu.au),
    School of Information Technology,
    Deakin University, Australia.
*/

int led_high = 0;  // variable to flag ON (1) or OFF (0)
int slp_sec = 0;  // variable holds number of seconds to sleep


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);      // set LED pin as output
  digitalWrite(LED_BUILTIN, LOW);    // switch off LED pin

  // Baud rate (speed of communication, symbol transfer rate)
  Serial.begin(9600);
}

void loop() {
  // sleep randomly selected 1 t0 5 seconds
  slp_sec = random(1, 5);
  
  if (led_high == 0) {
    // Write sleeping duration to serial monitor
    Serial.println("1 -> " + String(slp_sec) + " sec");
    // Write HIGH to LED
    digitalWrite(LED_BUILTIN, HIGH);

  } else {
    // Write sleeping duration to serial monitor
    Serial.println("0 -> " + String(slp_sec) + " sec");
    // Write LOW to LED
    digitalWrite(LED_BUILTIN, LOW);
  }
  
  // Switch LOW to HIGH
  led_high = (led_high + 1) % 2;

  // Sleep for a while
  delay(1000*slp_sec);
}
