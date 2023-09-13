#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#include <SoftwareSerial.h>

// WiFi credentials
#define SID "Tesla IoT"
#define PWD "fsL6HgjN"

// MQTT credentials
#define HOST "145.24.222.142"
#define MQTTPORT 8001
#define POSTTOPIC "/bots/hardware/1"
#define SUBTOPIC "/bots/hardware/1/path"
#define USERNAME "bread"
#define PASSWORD "enjoyers"

#define MESSAGE_LENGTH 20
#define MAX_MSG_LEN 128 

static char message[MESSAGE_LENGTH];

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient); 

SoftwareSerial commSerial(4, 5); // RX, TX

void setup() {
  Serial.begin(115200);
  commSerial.begin(115200);
  
  initWifi();

  // Set mqtt parameters
  mqttClient.setServer(HOST, MQTTPORT);
  mqttClient.setCallback(callback);    // Set the callback function 
  delay(100);
}

void loop() {
  // connect MQTT
  if (!mqttClient.connected()) {
    connectMqtt();
  }
  
  mqttClient.loop();
  
  delay(300);

  // Read message from commSerial
  while (commSerial.available() > 0) {
    static unsigned int message_pos = 0;

    char inByte = commSerial.read();

    if (inByte != '\n' && (message_pos < MESSAGE_LENGTH - 1) ) {
      message[message_pos] = inByte;
      message_pos++;
    } else {
      message[message_pos] = '\0';
      Serial.print("Message received: ");
//      mqttClient.publish(TESTTOPIC, message);
      Serial.println(message);
      message_pos = 0;    
    }
  }
}

void callback(char *msgTopic, byte *msgPayload, unsigned int msgLength) {
  static char message[MAX_MSG_LEN+1];
  if (msgLength > MAX_MSG_LEN) {
    msgLength = MAX_MSG_LEN;
  }
  strncpy(message, (char*)msgPayload, msgLength);
  message[msgLength] = '\0';
  Serial.print("Topic ");
  Serial.print(msgTopic);
  Serial.print(", message received: ");
  Serial.println(message);
//  mqttClient.publish(TESTTOPIC, message);
  commSerial.write(message);
}

void initWifi() {
  WiFi.begin(SID, PWD);
  Serial.print("Connecting to WiFi ..");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  Serial.print("\nConnected to WiFi access point with ip: ");
  Serial.println(WiFi.localIP());
}

void connectMqtt() {
  String clientId = "hardware-";
  clientId += String(random(0xff), HEX);
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // Attempt to connect
    if (mqttClient.connect(clientId.c_str(), USERNAME, PASSWORD)) { 
      Serial.println("connected");
      mqttClient.subscribe(SUBTOPIC); // Subscribe to the topic with qos 1
      mqttClient.subscribe(TESTTOPIC);
    } 
    else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
