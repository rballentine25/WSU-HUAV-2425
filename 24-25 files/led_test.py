'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

import RPi.GPIO as GPIO
from time import sleep

# define the led pin: here using PWM0, GPIO18/pin 12
ledpin = 12				        # PWM pin connected to LED

GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system
GPIO.setup(ledpin,GPIO.OUT)

# creating a PWM object: GPIO.PWM(pin no, frequency)
pi_pwm = GPIO.PWM(ledpin,1000)	#create PWM instance with frequency
# start(duty cycle %) starts the pwm generation, here with duty cycle of 0% (HIGH 0% of time)
pi_pwm.start(0)				    #start PWM of required Duty Cycle 

while True:
    # first for loop increases duty cycle from 0 to 100 (off to 100 brightness)
    # second for loop decreases duty cycle from 100 to 0 (full brightness to off)

    # following loop will go from 0 to 100 by increments of 1
    for duty in range(0,101,1):
        # increase duty cycle by 1% every for loop iteration
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
        sleep(0.01)
    sleep(0.5)
    
    for duty in range(100,-1,-1):
        pi_pwm.ChangeDutyCycle(duty)
        sleep(0.01)
    sleep(0.5)