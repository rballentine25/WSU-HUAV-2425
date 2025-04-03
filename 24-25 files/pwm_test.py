'''
Code from electronicwings.com for an LED circuit with PWM
http://www.electronicwings.com
'''
# PWM set up for Genset test 

import RPi.GPIO as GPIO
from time import sleep
from gpiozero import LED, PWMLED


gentoload_pin = 20 #gpio20, pin 38
MCpwr_pin = 21 #gpio21, pin 40
res6_pin = 26 #gpio19, pin 35
pwm_pwr_pin = 13 #gpio18, pin 12

gentoload = LED(gentoload_pin)
MCpwr = LED(MCpwr_pin)
res6 = LED(res6_pin)

gentoload.on()
MCpwr.on()
res6.on()

# define the led pin: here using PWM0, GPIO18/pin 12
# RS motor is 12, LS motor is 33
# RS motor starts turning at 40%. LS motor starts turning at 45% 
# reverse for motor is switch in | setting
outpin = 18				        # PWM pin connected to LED

GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BCM)		#set pin numbering system
GPIO.setup(outpin,GPIO.OUT)

# creating a PWM object: GPIO.PWM(pin no, frequency)
# frequency was whatever was already in the elctronicwings code
pi_pwm = GPIO.PWM(outpin,1000)	#create PWM instance with frequency

# start(duty cycle %) starts the pwm generation, here with duty cycle of 0% (HIGH 0% of time)
pi_pwm.start(0)				    #start PWM of required Duty Cycle 

while True:
    # first for loop increases duty cycle from 35 to 100 power
    # second for loop decreases duty cycle from 100 to 50% power
    # first test was 0-100 and genset didn't 

    # following loop will go from 35 to 100 by increments of 5
    for duty in range(35,71,5):
        # increase duty cycle by 5% every for loop iteration
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 35-100
        print("increasing to ", duty, "%")
        # incrememnt every 5 sec
        sleep(5)

    # run at 100% duty cycle for 10 sec
    sleep(5)

    # decrease duty cycle from 100 to 50 by 5's, pausing every 2 secs
    for duty in range(70,0,-5):
        pi_pwm.ChangeDutyCycle(duty)
        sleep(2)

    break
    
    