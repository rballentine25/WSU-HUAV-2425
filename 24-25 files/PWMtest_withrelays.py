from gpiozero import LED, PWMLED
from time import sleep
import RPi.GPIO as GPIO

# THIS IS THE SCRIPT THAT USES THE 
# WRONG LIBRARY!!!!!! DONT USE THIS ONE

GPIO.setmode(GPIO.BCM)		    #set pin numbering system to broadcom (GPIO)
# output pin for the PWM signal: should be either 18 (RHS) or 19 (LHS)
outpin = 18			       

GPIO.setwarnings(False)			#disable warnings
GPIO.setup(outpin,GPIO.OUT)

# identifying pins
# gentoload = LED(5)
# MCpwr = LED(16)
# res6 = LED(27)
sgcontrol = LED(20)

# gentoload.on()
# MCpwr.on()
# res6.on()
sgcontrol.on()

# creating a PWM object: GPIO.PWM(pin no, frequency)
# frequency was whatever was already in the elctronicwings code
pi_pwm = GPIO.PWM(outpin,1000)	#create PWM instance with frequency

# start(duty cycle %) starts the pwm generation, here with duty cycle of 0% (HIGH 0% of time)
# pi_pwm.start(1)				    #start PWM of required Duty Cycle 

print("starting")
pi_pwm.start(100)  # changing to 70%
sleep(30)
#input('Press Return to Stop:')
pi_pwm.ChangeDutyCycle(0)   # changing back to 0%
pi_pwm.stop()
GPIO.cleanup()

# turning off relays
# gentoload.off()
# MCpwr.off()
# res6.off()
sgcontrol.off()
