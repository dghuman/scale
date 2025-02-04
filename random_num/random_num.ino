const int HANDSHAKE = 0;
const int VOLTAGE_REQUEST = 1;
const int ON_REQUEST = 2;
const int STREAM = 3;
const int READ_DAQ_DELAY = 4;

// Initially, only send data upon request
int daqMode = ON_REQUEST;

// Default time between data acquisition is 100 ms
int daqDelay = 100;

// String to store input of DAQ delay
String daqDelayStr;


// Keep track of last data acquistion for delays
unsigned long timeOfLastDAQ = 0;


unsigned long printVoltage() {
  // Read value from analog pin
  long value = random(100);

  // Get the time point
  unsigned long timeMilliseconds = millis();

  // Write the result
  if (Serial.availableForWrite()) {
    String outstr = String(String(timeMilliseconds, DEC) + "," + String(value));
    Serial.println(outstr);
  }

  // Return time of acquisition
  return timeMilliseconds;
}


void setup() {
  // Initialize serial communication
  Serial.begin(115200);
}


void loop() {
  // If we're streaming
  if (daqMode == STREAM) {
    if (millis() - timeOfLastDAQ >= daqDelay) {
      timeOfLastDAQ = printVoltage();
    }
  }

  // Check if data has been sent to Arduino and respond accordingly
  if (Serial.available() > 0) {
    // Read in request
    int inByte = Serial.read();

    // If data is requested, fetch it and write it, or handshake
    switch(inByte) {
      case VOLTAGE_REQUEST:
        timeOfLastDAQ = printVoltage();
        break;
      case ON_REQUEST:
        daqMode = ON_REQUEST;
        break;
      case STREAM:
        daqMode = STREAM;
        break;
      case READ_DAQ_DELAY:
        // Read in delay, knowing it is appended with an x
        daqDelayStr = Serial.readStringUntil('x');

        // Convert to int and store
        daqDelay = daqDelayStr.toInt();

        break;
      case HANDSHAKE:
        if (Serial.availableForWrite()) {
          Serial.println("Message received.");
        }
        break;
    }
  }
}