#include <Wire.h>
#include <Adafruit_MCP4725.h>

// as of right now this only works in the Arduino IDE bc of the Adafruit library
// if i can a) download the Arduino IDE or b) figure out to load it into VScode, i can run it on my own laptop


#define DAC_ADDRESS 0x62  // Default I2C address of the MCP4725 DAC
#define MOTOR_PIN 9       // Example PWM pin connected to the motor controller

// create instance of Adafruit_MCP4725 class named dac
Adafruit_MCP4725 dac;


void setup() {
// Serial initializes serial comm between Arduino and connected device (9600 bits/sec)
 Serial.begin(9600);

// begin method: begins hardware and checks the DAC was found
 dac.begin(DAC_ADDRESS);

// setVoltage(output, writeEEPROM, i2c_frequency) is a bool return method that 
// sets output voltage to a fraction of source vref. 
 dac.setVoltage(0, false);  // Set DAC voltage to 0V initially

// sets pin 9 as output
 pinMode(MOTOR_PIN, OUTPUT);

// analogWrite: controls speed of motor
// incrementally increases voltage up to 2000 (~4V), with 50ms delay in between each step
// (should take 2s in total)
for (int voltage = 0; voltage <= 2000; voltage += 50) {
   // first param specifies new voltage setting, second is for whether this setting is stored
   // on DAC's memory (DAC retains value after Arduino power down if true)
   dac.setVoltage(voltage, false);

   // analogWrite generates a PWM signal on the specified pin using map() function to scale
   // DAC voltage to PWM signal between 0-130 (max is 255)
   analogWrite(MOTOR_PIN, map(voltage, 0, 2000, 0, 130));
   delay(50);  // Adjust the delay as needed for your application
 }
}

// voltage should be set to 2000 by this point
// loop code is the only thing that keeps executing after initial setup is completed
void loop() {

 // If the duration has not been reached, stay at 4V
 // this code is always true because the if condition is assigning voltage = 2000?
 // should prob be if(voltage == 2000)
 if(int voltage == 2000) {
   Serial.println("Staying at 4V");
   Serial.println(voltage);

   // reassigns dac voltage to 2000- not really necessary?
   dac.setVoltage(voltage, false);
   Serial.println(voltage);

  // maintains motor speed
   analogWrite(MOTOR_PIN, 130);
   Serial.println("Start Delay");

   // delay of 60s
   delay(60000);
   Serial.println("Staying at 4V completed");
}


}
