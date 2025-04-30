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
res7 = LED(17)
sgcontrol = LED(20)
gentobatt = LED(6)
batttoload = LED(0)
battneg = LED(21)

start_pin = 18		
ICE_pin = 19  

GPIO.setwarnings(False)			
GPIO.setmode(GPIO.BCM)		    
GPIO.setup(ICE_pin,GPIO.OUT)

ICE_pwm = GPIO.PWM(ICE_pin,2000)	
ICE_pwm.start(0)  

GPIO.setwarnings(False)			
GPIO.setmode(GPIO.BCM)		    
GPIO.setup(start_pin,GPIO.OUT)

SG_pwm = GPIO.PWM(start_pin,2000)	
SG_pwm.start(0)  

df = pd.read_excel('your_file.xlsx')

length = df.shape[0]
df.columns = ['Realtive Time', 'Power Level', 'Mode of Opperation']     

for k in range(0,length,1):
    mode = df.iloc[k,2]
    load = df.iloc[k,1]

    if mode == 0:
        gentoload.off()
        MCpwr.off()
        sgcontrol.off()
        gentobatt.off()
        batttoload.on()
        battneg.on()
        
        
    elif mode == 1:
        sgcontrol.off()
        gentobatt.off()
        batttoload.off()
        battneg.off()
        gentoload.on()
        MCpwr.on()

        if mode != df.iloc[k-1,2]:
            ICE_pwm.ChangeDutyCycle(100)

    elif mode == 2:
        a = 1
    else:
        print('mode outside avaible modes')

    if load == 7:
        res2.off()
        res3.off()
        res4.off()
        res5.off()
        res6.off()
        res7.off()
        res1.on()
    elif load == 6:
        res1.off()
        res3.off()
        res4.off()
        res5.off()
        res6.off()
        res7.off()
        res2.on()
    elif load == 5:
        res1.off()
        res2.off()
        res4.off()
        res5.off()
        res6.off()
        res7.off()
        res3.on()
    elif load == 4:
        res1.off()
        res2.off()
        res3.off()
        res5.off()
        res6.off()
        res7.off()
        res4.on()
    elif load == 3:
        res1.off()
        res2.off()
        res3.off()
        res4.off()
        res6.off()
        res7.off()
        res5.on()
    elif load == 2:
        res1.off()
        res2.off()
        res3.off()
        res4.off()
        res5.off()
        res7.off()
        res6.on()
    elif load == 1:
        res1.off()
        res2.off()
        res3.off()
        res4.off()
        res5.off()
        res6.off()
        res7.on()
    else:
        print('Load outside avalible range')
            
    sleep(0.5)

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

GPIO.cleanup()       