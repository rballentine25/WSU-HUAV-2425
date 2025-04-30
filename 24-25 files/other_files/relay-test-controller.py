import RPi.GPIO as GPIO
from time import sleep
from gpiozero import LED, PWMLED


# identifying pins
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

gentobatt.on()
MCpwr.on()
res6.on()

input('Press Return to start discharge')

batttoload.on()
battneg.on()

input('Press Return to turn off relays:')

gentoload.off()
MCpwr.off()
res6.off()