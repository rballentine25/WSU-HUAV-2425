from gpiozero import LED, PWMLED
from time import sleep
import RPi.GPIO as GPIO


gentoload_pin = 20 #gpio20, pin 38
MCpwr_pin = 21 #gpio21, pin 40
res6_pin = 19 #gpio19, pin 35
pwm_pwr_pin = 18 #gpio18, pin 12

gentoload = LED(gentoload_pin)
MCpwr = LED(MCpwr_pin)
res6 = LED(res6_pin)

gentoload.on()
MCpwr.on()
res6.on()



pwr_pin = PWMLED(pwm_pwr_pin)
while True:
    # first for loop increases duty cycle from 35 to 100 power
    # second for loop decreases duty cycle from 100 to 50% power
    # first test was 0-100 and genset didn't 

    # following loop will go from 35 to 100 by increments of 5
    for duty in range(50,101,5):
        # increase duty cycle by 5% every for loop iteration
        pwr_pin.value = duty/100 #provide duty cycle in the range 35-100
        print("increasing to ", duty, "%")
        # incrememnt every 5 sec
        sleep(5)

    # run at 100% duty cycle for 10 sec
    sleep(5)

    # decrease duty cycle from 100 to 50 by 5's, pausing every 2 secs
    for duty in range(100,49,-5):
        pwr_pin.value = duty/100
        sleep(2)

    pwr_pin.off()
    break


gentoload.off()
MCpwr.off()
res6.off()

