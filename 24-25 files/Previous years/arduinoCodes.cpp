#include <Wire.h>
#include <Adafruit_MCP4725.h>

// as of right now this only works in the Arduino IDE bc of the Adafruit library
// if i can a) download the Arduino IDE or b) figure out to load it into VScode, i can run it on my own laptop


#define DAC_ADDRESS 0x62  // Default I2C address of the MCP4725 DAC
#define MOTOR_PIN 9       // Example PWM pin connected to the motor controller


Adafruit_MCP4725 dac;




void setup() {
 Serial.begin(9600);


 dac.begin(DAC_ADDRESS);
 dac.setVoltage(0, false);  // Set DAC voltage to 0V initially


 pinMode(MOTOR_PIN, OUTPUT);


for (int voltage = 0; voltage <= 2000; voltage += 50) {
   dac.setVoltage(voltage, false);
   analogWrite(MOTOR_PIN, map(voltage, 0, 2000, 0, 130));
   delay(50);  // Adjust the delay as needed for your application
 }
}
void loop() {


 // If the duration has not been reached, stay at 5V
 if(int voltage = 2000) {
   Serial.println("Staying at 4V");
   Serial.println(voltage);
   dac.setVoltage(voltage, false);
   Serial.println(voltage);
   analogWrite(MOTOR_PIN, 130);
   Serial.println("Start Delay");
   delay(60000);
   Serial.println("Staying at 4V completed");




}


}
