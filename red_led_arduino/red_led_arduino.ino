const int HANDSHAKE = 0;
const int LED_OFF = 1;
const int LED_ON = 2;


void setup() {
  pinMode(LED_RED, OUTPUT);

  // initialize serial communication
  Serial.begin(115200);
}


void loop() {
  // Check if data has been sent to Arduino and respond accordingly
  if (Serial.available() > 0) {
    // Read in request
    int inByte = Serial.read();

    // Take appropriate action
    switch(inByte) {
      case LED_ON:
        digitalWrite(LED_RED, LOW);
        break;
      case LED_OFF:
        digitalWrite(LED_RED, HIGH);
        break;
      case HANDSHAKE:
        if (Serial.availableForWrite()) {
          Serial.println("Message received.");
        }
        break;
    }
  }
}