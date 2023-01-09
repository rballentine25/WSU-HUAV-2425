#%% import libraries
import time
import numpy as np
import math as mt
import keyboard
import pyfirmata

print('Motor wires: white=signal, black=GND, ensure ESC power is connected to flight controller')
print('Motor 1 signal connect to digital pin 2:')
print('Motor 2 signal connect to digital pin 3:')
print('Motor 3 signal connect to digital pin 4:')
print('Motor 4 signal connect to digital pin 5:')
print('Motor black wires connected to common ground with Arduino')
input('Connections as above? Enter to skip')

print('Press Enter to Arm ESC:')
input('Press Enter to Arm ESC:')

# set up the throttling function and arduino board
def throttle():
    global PERCENT
    percent = PERCENT/100
    if (percent>=0) & (percent<=1):
        percent = percent
    elif percent<0:
        percent=0
        print('Throttle Command Is Out Of Range!')
    elif percent>1:
        percent=1
        print('Throttle Command Is Out Of Range!')
    angle = percent*180
    ESC1.write(angle)
    ESC2.write(angle)
    ESC3.write(angle)
    ESC4.write(angle)
    

board = pyfirmata.Arduino('COM7')
  
# setup the ESC on pin 2
PERCENT  = 0        # initial throttle percent
dP = 5                          # percent throttle change per keypress

ESC1 = board.get_pin('d:2:s') # pin to communicate to the ESC with
ESC2 = board.get_pin('d:3:s')
ESC3 = board.get_pin('d:4:s')
ESC4 = board.get_pin('d:5:s')
board.servo_config(2,1000,2000,1500) # Arm the ESC
board.servo_config(3,1000,2000,1500)
board.servo_config(4,1000,2000,1500)
board.servo_config(5,1000,2000,1500)

throttle()

print('Press Enter to Begin Manual Control:')
input('Press Enter to Begin Manual Control:')
print('UP/DOWN arrows to increase/decrease throttle of all four motors')
print('RIGHT/LEFT arrows to increase/decrease delta-throttle')
print('ESC or R to quit or reset (emergency only, may damage components)', '\n')

time.sleep(0.2)
print('Throttle (%): ', PERCENT)
print('Delta-Throttle (%): ', dP)

# while loop 
while True:

    if keyboard.is_pressed('up_arrow'):
            PERCENT = PERCENT + dP
            throttle()
            print('Delta-Throttle (%): ', dP)
            print('Throttle (%): ', PERCENT)
            time.sleep(0.2)
    
    elif keyboard.is_pressed('down_arrow'):
            PERCENT = PERCENT - dP
            throttle()
            print('Delta-Throttle (%): ', dP)
            print('Throttle (%): ', PERCENT)
            time.sleep(0.2)            
    
    elif keyboard.is_pressed('right_arrow'):
        dP = dP + 1
        print('Delta-Throttle (%): ', dP)
        time.sleep(0.2)
   
    elif keyboard.is_pressed('left_arrow'):
        dP = dP - 1
        print('Delta-Throttle (%): ', dP)
        time.sleep(0.2)
    
    elif keyboard.is_pressed('r'):
        dP = 5
        PERCENT=0
        throttle()
        print('Initial Conditions Reset!')
        print('Throttle (%): ', PERCENT)
        print('Delta Throttle (%): ', dP)
        time.sleep(0.2)  

    elif keyboard.is_pressed('esc'): 
        dP = 5
        PERCENT=0
        throttle()
        print('Quitting Script Now!')
        break


# %%
