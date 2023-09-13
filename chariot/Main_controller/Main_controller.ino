// include libraries
#include <Adafruit_PWMServoDriver.h>
#include <VL53L0X.h>
#include <SoftwareSerial.h>

// servo driver
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// ToF sensor
VL53L0X lox;

// define servo data
#define SERVOMIN 94
#define SERVOMAX 500
#define SERVO_FREQ 50

// rotation speed
#define ROTATION90DEGREES 500
#define ROTATION180DEGREES 1000

// set servo pins
uint8_t servonum_0 = 0;
uint8_t servonum_1 = 1;
uint8_t servonum_2 = 2;

// variables distance data
int distanceData[] = { 134, 2, 3 };

// [distance left, distance forward, distance right]
int array_length = sizeof(distanceData) / sizeof(int);
String distanceSensorData = "";

String direction = "up";

void setup() {
  // Setup serial 
  Serial.begin(115200);

  // Initialize the PWM and servo shield 
  pwm.begin();

  // Set the PWM frequency (usually 50 Hz for servos) 
  pwm.setPWMFreq(SERVO_FREQ);

  delay(10);

  // Setup ToF sensor 
  lox.init();
  lox.setTimeout(500);
  lox.startContinuous();

  // center sensor servo, ToF sensor looking forward 
  pwm.setPWM(servonum_0, 0, angle_to_pulse(90));
}

uint16_t angle_to_pulse(int angles) {
  float pulse_len;
  // 0 degree leads to SERVOMIN (should be 1000 uS) 
  // 180 degrees leads to SERVOMAX (should be 2000 uS) 
  // anything in the middle is linearly integrated 
  angles = constrain(angles, 0, 180);
  // to be safe (memory 32632) 
  pulse_len = SERVOMIN + (SERVOMAX - SERVOMIN) / 180.0 * float(angles);
  return (pulse_len);
}

// reads the sensor data and put is into an array
void get_distance_array() {
  // set sensor servo to 0, 90 and 180 degrees, scans the distance and put them into a array 
  for (int angles = 0; angles <= 180; angles += 90) {
    pwm.setPWM(servonum_0, 0, angle_to_pulse(angles));
    distanceData[angles / 90] = lox.readRangeContinuousMillimeters();
    delay(1000);
  }
  pwm.setPWM(servonum_0, 0, angle_to_pulse(90));
  print_sensor_data();
}

// print the sensor data as one String in the commSerial
void print_sensor_data() {
  for (int i = 0; i < array_length; i++) {
    distanceSensorData += String(distanceData[i]);

    // Add separator 
    if (i < array_length - 1) {
      distanceSensorData += ";";
    }
  }
  // Serial.println(distanceSensorData);
  distanceSensorData = "";
}

void drive_forward() {
  // servo 1 angle_to_pulse(75) rotate forward, servo 2 angle_to_pulse(120) rotate forward 
  pwm.setPWM(servonum_1, 0, angle_to_pulse(75));
  pwm.setPWM(servonum_2, 0, angle_to_pulse(120));
  delay(500);
  drive_stop();
}

void drive_backward() {
  // servo 1 angle_to_pulse(120) rotate backward, servo 2 angle_to_pulse(75) rotate backward 
  pwm.setPWM(servonum_1, 0, angle_to_pulse(120));
  pwm.setPWM(servonum_2, 0, angle_to_pulse(75));
  delay(500);
  drive_stop();
}

void drive_right(int duration) {
  // servo 1 angle_to_pulse(120) rotate backward, servo 2 angle_to_pulse(120) rotate forward 
  pwm.setPWM(servonum_1, 0, angle_to_pulse(120));
  pwm.setPWM(servonum_2, 0, angle_to_pulse(120));
  delay(duration);
  drive_stop();
}

void drive_left(int duration) {
  // servo 1 angle_to_pulse(75) rotate forward, servo 2 angle_to_pulse(75) rotate backward 
  pwm.setPWM(servonum_1, 0, angle_to_pulse(75));
  pwm.setPWM(servonum_2, 0, angle_to_pulse(75));
  delay(duration);
  drive_stop();
}

void drive_stop() {
  // servo 1 angle_to_pulse(100) stop rotating, servo 2 angle_to_pulse(100) stop rotating 
  pwm.setPWM(servonum_1, 0, angle_to_pulse(100));
  pwm.setPWM(servonum_2, 0, angle_to_pulse(100));
}

void checkDir(String curDir, String dir) {
  int str_len = curDir.length() + 1;
  char ch_arr[str_len];
  curDir.toCharArray(ch_arr, str_len);

  int str_lenght = dir.length() + 1;
  char char_arr[str_lenght];
  dir.toCharArray(char_arr, str_lenght);

  Serial.println(ch_arr);
  Serial.println(char_arr);
  
  if(strcmp(ch_arr, char_arr) != 0) {
    if (strcmp(ch_arr, "up") == 0 && strcmp(char_arr, "right") == 0) {
      drive_right(ROTATION90DEGREES);
      direction = "right";
    }
    else if(strcmp(ch_arr, "up") == 0 && strcmp(char_arr, "left") == 0) {
      drive_left(ROTATION90DEGREES);
      direction = "left";
    }
    else if(strcmp(ch_arr, "right") == 0 && strcmp(char_arr, "down") == 0) {
      drive_right(ROTATION90DEGREES);
      direction = "down";
    }
    else if(strcmp(ch_arr, "right") == 0 && strcmp(char_arr, "up") == 0) {
      drive_left(ROTATION90DEGREES);
      direction = "up";
    }
    else if(strcmp(ch_arr, "down") == 0 && strcmp(char_arr, "left") == 0) {
      drive_right(ROTATION90DEGREES);
      direction = "left";
    }
    else if(strcmp(ch_arr, "down") == 0 && strcmp(char_arr, "right") == 0) {
      drive_left(ROTATION90DEGREES);
      direction = "right";
    }
    else if(strcmp(ch_arr, "left") == 0 && strcmp(char_arr, "up") == 0) {
      drive_right(ROTATION90DEGREES);
      direction = "up";
    }
    else if(strcmp(ch_arr, "left") == 0 && strcmp(char_arr, "down") == 0) {
      drive_left(ROTATION90DEGREES);
      direction = "down";
    }
    else {
      drive_right(ROTATION180DEGREES);
      if(strcmp(ch_arr, "up") == 0) {
        direction = "down";
      }
      else if(strcmp(ch_arr, "right") == 0) {
        direction = "left";
      }
      else if(strcmp(ch_arr, "down") == 0) {
        direction = "up";
      }
      else if(strcmp(ch_arr, "left") == 0) {
        direction = "right";
      }
    }
  }
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    // Serial.println(data);
    int str_len = data.length();
    char ch_arr[str_len];
    data.toCharArray(ch_arr, str_len);
    // int result = strcmp(ch_arr, "Read sensor"); 
    // Serial.println(result); 

    if (strcmp(ch_arr, "check") == 0) {
      get_distance_array();
    }
    else if (strcmp(ch_arr, "forward") == 0) {
      drive_forward();
    }
    else if (strcmp(ch_arr, "backward") == 0) {
      drive_backward();
    }
    else if (strcmp(ch_arr, "stop") == 0) {
      drive_stop();
    }
    else if (strcmp(ch_arr, "left") == 0) {
      Serial.println("LEFT");
      checkDir(direction, "left");
    }
    else if (strcmp(ch_arr, "right") == 0) {
      Serial.println("RIGHT");
      checkDir(direction, "right");
    }
    else if (strcmp(ch_arr, "up") == 0) {
      Serial.println("UP");
      checkDir(direction, "up");
    }
    else if (strcmp(ch_arr, "down") == 0) {
      Serial.println("DOWN");
      checkDir(direction, "down");
    }
    Serial.println(direction);
  }
}
