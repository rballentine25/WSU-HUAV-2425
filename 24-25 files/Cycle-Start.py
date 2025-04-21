# Cycle code

import RPi.GPIO as GPIO
from time import sleep
from gpiozero import LED, PWMLED
import pandas as pd

gentoload = LED(5)
MCpwr = LED(16)
res1 = LED(24)
res2 = LED(23)
res3 = LED(15)
res4 = LED(14)
res5 = LED(22)
res6 = LED(27)
sgcontrol = LED(20)

gentoload.on()
MCpwr.on()
res6.on()
sgcontrol.on()

outpin = 18		       

GPIO.setwarnings(False)			
GPIO.setmode(GPIO.BCM)		    
GPIO.setup(outpin,GPIO.OUT)

pi_pwm = GPIO.PWM(outpin,2000)	
pi_pwm.start(0)  

while True:

    for duty in range(50,101,1):
        pi_pwm.ChangeDutyCycle(duty) 
        print("increasing to ", duty, "%")
        sleep(.1)

    sleep(2)

    for duty in range(100,50,-1):
        pi_pwm.ChangeDutyCycle(duty)
        print("decreasing to ", duty, "%")
        sleep(.1)

    break

pi_pwm.stop()      

gentoload.off()
MCpwr.off()
res6.off()
sgcontrol.off()

GPIO.cleanup()       