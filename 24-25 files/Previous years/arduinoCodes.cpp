#include <Wire.h>
#include <Adafruit_MCP4725.h>

// as of right now this only works in the Arduino IDE bc of the Adafruit library
// if i can a) download the Arduino IDE or b) figure out to load it into VScode, i can run it on my own laptop


#define DAC_ADDRESS 0x62  // Default I2C address of the MCP4725 DAC
#define MOTOR_PIN 9       // Example PWM pin connected to the motor controller

// create instance of Adafruit_MCP4725 class named dac
Adafruit_MCP4725 dac;


void setup() {
// serial? connected output device?
 Serial.begin(9600);

// begin method: begins hardware and checks the DAC was found
// takes in the I2C of the dac, which defaults to 0x62
// also takes in the I2C TwoWire object, which defaults to &Wire
 dac.begin(DAC_ADDRESS);

// setVoltage(output, writeEEPROM, i2c_frequency) is a bool return method that 
// sets output voltage to a fraction of source vref. 
// output is 12bit value for DAC input to output voltage (uint16_t)
// writeEEPROM: if true, 'output' will also be written to MCP4725's internal memory
// (DAC will retain curr volt after power down)
// i2c_freq sets I2C clock when writing to DAC, default set to 400KHz
 dac.setVoltage(0, false);  // Set DAC voltage to 0V initially


 pinMode(MOTOR_PIN, OUTPUT);


// analogWrite: controls speed of motor
// incrementally increases voltage up to 2000, with 50ms delay in between each step
for (int voltage = 0; voltage <= 2000; voltage += 50) {
   dac.setVoltage(voltage, false);
   analogWrite(MOTOR_PIN, map(voltage, 0, 2000, 0, 130));
   delay(50);  // Adjust the delay as needed for your application
 }
}

// voltage should be set to 2000 by this point
void loop() {

 // If the duration has not been reached, stay at 5V
 if(int voltage = 2000) {
   Serial.println("Staying at 4V");
   Serial.println(voltage);

   dac.setVoltage(voltage, false);
   Serial.println(voltage);

   analogWrite(MOTOR_PIN, 130);
   Serial.println("Start Delay");

   // delay of 60s
   delay(60000);
   Serial.println("Staying at 4V completed");
}


}
