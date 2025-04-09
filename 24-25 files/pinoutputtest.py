import RPi.GPIO as GPIO
import time
from gpiozero import LED

# USED TO TEST RELAYS 

# using GPIO pin numbering
currpin = 24

# turns signal on (3.3v) for x seconds then turns off
pin = LED(currpin)

pin.on()
time.sleep(5)
pin.off()