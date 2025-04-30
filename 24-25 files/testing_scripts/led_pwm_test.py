import RPi.GPIO as GPIO
from time import sleep
from gpiozero import LED, PWMLED

# TO TEST LED CIRCUITS

# output pin for the PWM signal: should be either 18 (RHS) or 19 (LHS)
outpin = 18			       

GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BCM)		    #set pin numbering system to broadcom (GPIO)
GPIO.setup(outpin,GPIO.OUT)

# creating a PWM object: GPIO.PWM(pin no, frequency)
# frequency was whatever was already in the elctronicwings code
pi_pwm = GPIO.PWM(outpin,1000)	
pi_pwm.start(0)  

n = 0
while True:
    # first for loop increases duty cycle from 35 to 100 power
    # second for loop decreases duty cycle from 100 to 50% power
    # first test was 0-100 and genset didn't 

    # following loop will go from 35 to 100 by increments of 5
    for duty in range(0,101,5):
        # increase duty cycle by 5% every for loop iteration
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 35-100
        #print("increasing to ", duty, "%")
        # incrememnt every 5 sec
        sleep(.1)

    # run at 100% duty cycle for 10 sec
    sleep(.5)

    # decrease duty cycle from 100 to 50 by 5's, pausing every 2 secs
    for duty in range(100,0,-5):
        pi_pwm.ChangeDutyCycle(duty)
        #print("decreasing to ", duty, "%")
        sleep(.1)

    n=n+1
    if n == 5:
        break

pi_pwm.stop()     