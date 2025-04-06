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
gentoload = LED(5)
MCpwr = LED(16)
res6 = LED(27)
#sgcontrol = LED(20)

gentoload.on()
MCpwr.on()
res6.on()
# sgcontrol.on()



# output pin for the PWM signal: should be either 18 (RHS) or 19 (LHS)
outpin = 19			       

GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BCM)		    #set pin numbering system to broadcom (GPIO)
GPIO.setup(outpin,GPIO.OUT)

# creating a PWM object: GPIO.PWM(pin no, frequency)
# frequency was whatever was already in the elctronicwings code
pi_pwm = GPIO.PWM(outpin,1000)	#create PWM instance with frequency

# start(duty cycle %) starts the pwm generation, here with duty cycle of 0% (HIGH 0% of time)
# pi_pwm.start(1)				    #start PWM of required Duty Cycle 

print("starting")
pi_pwm.start(70)  # changing to 70%
sleep(5)
#input('Press Return to Stop:')
pi_pwm.ChangeDutyCycle(0)   # changing back to 0%
pi_pwm.stop()
GPIO.cleanup()

pi_pwm.stop()
GPIO.cleanup()

# turning off relays
gentoload.off()
MCpwr.off()
res6.off()
#sgcontrol.off()


# LOOP TO AMP UP THEN DOWN 

# while True:
#     # first for loop increases duty cycle from 35 to 100 power
#     # second for loop decreases duty cycle from 100 to 50% power
#     # first test was 0-100 and genset didn't 

#     # following loop will go from 35 to 100 by increments of 5
#     for duty in range(35,71,5):
#         # increase duty cycle by 5% every for loop iteration
#         pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 35-100
#         print("increasing to ", duty, "%")
#         # incrememnt every 5 sec
#         sleep(5)

#     # run at 100% duty cycle for 10 sec
#     sleep(5)

#     # decrease duty cycle from 100 to 50 by 5's, pausing every 2 secs
#     for duty in range(70,0,-5):
#         pi_pwm.ChangeDutyCycle(duty)
#         sleep(2)

#     break
    
    