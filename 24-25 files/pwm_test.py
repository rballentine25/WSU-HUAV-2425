'''
Code from electronicwings.com for an LED circuit with PWM
http://www.electronicwings.com
'''
# PWM set up for Genset test 
# USE THIS ONE

import RPi.GPIO as GPIO
from time import sleep
from gpiozero import LED, PWMLED


# identifying pins
# gentoload = LED(5)
# MCpwr = LED(16)
# res6 = LED(27)
sgcontrol = LED(20)

# gentoload.on()
# MCpwr.on()
# res6.on()
sgcontrol.on()

# output pin for the PWM signal: should be either 18 (RHS) or 19 (LHS)
outpin = 18		       

GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BCM)		    #set pin numbering system to broadcom (GPIO)
GPIO.setup(outpin,GPIO.OUT)

# creating a PWM object: GPIO.PWM(pin no, frequency)
# frequency was whatever was already in the elctronicwings code
pi_pwm = GPIO.PWM(outpin,2000)	
pi_pwm.start(0)  

#start PWM 
# print("starting")
# pi_pwm.start(0)                # starting at 50
# pi_pwm.ChangeDutyCycle(50)
# sleep(10)
# #input('press enter to continue:')                       # sending signal for 20 secs
# pi_pwm.ChangeDutyCycle(0)       # changing back to 0%
# pi_pwm.stop()                   # stopping the PWM signals

           # cleaning up

# LOOP TO AMP UP THEN DOWN 

while True:
    # first for loop increases duty cycle from 35 to 100 power
    # second for loop decreases duty cycle from 100 to 50% power
    # first test was 0-100 and genset didn't 

    # following loop will go from 35 to 100 by increments of 5
    for duty in range(50,101,1):
        # increase duty cycle by 5% every for loop iteration
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 35-100
        print("increasing to ", duty, "%")
        # incrememnt every 5 sec
        sleep(.1)

    # run at 100% duty cycle for 10 sec
    sleep(2)

    # decrease duty cycle from 100 to 50 by 5's, pausing every 2 secs
    for duty in range(100,50,-1):
        pi_pwm.ChangeDutyCycle(duty)
        print("decreasing to ", duty, "%")
        sleep(.1)

    break

pi_pwm.stop()      

# turning off relays
# gentoload.off()
# MCpwr.off()
# res6.off()
sgcontrol.off()

GPIO.cleanup()       