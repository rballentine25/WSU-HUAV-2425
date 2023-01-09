#%% import libraries
import time
import numpy as np
import math as mt
import keyboard
import pyfirmata

print('ESC wires: white=signal, small black=common GND')
print('ESC signal connect to digital pin 2:')
print('ESC small black wire connected to Arduino GND pin')
print('Connections as above? Enter to skip')
input('Props removed and all Connections as above and no power to ESC? Press enter to continue')

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
    

board = pyfirmata.Arduino('COM7')
PERCENT  = 0        # initial throttle percent
print(PERCENT, '%')

ESC1 = board.get_pin('d:2:s') # pin to communicate to the ESC with
board.servo_config(2,1000,2000,1500) # Arm the ESC
throttle() # Set throttle to zero

PERCENT = 100
print(PERCENT, '%')
throttle()

print('CAREFULLY Connect Power to ESC. Be warned that it may spark. DO NOT get your fingers in the way!!!')
print('Press enter when finished.')
input('CAREFULLY Connect Power to ESC. Be warned that it may spark. DO NOT get your fingers in the way!!!')

while True:

    if keyboard.is_pressed('up_arrow'):
        if PERCENT == 0:
            for t in range(0, 100):
                PERCENT = PERCENT + 1
                print(PERCENT, '%')
                throttle()
                time.sleep(0.01)
    
    elif keyboard.is_pressed('down_arrow'):
        if PERCENT == 100:
            for t in range(0, 100):
                PERCENT = PERCENT - 1
                print(PERCENT, '%')
                throttle()
                time.sleep(0.01)
    
    elif keyboard.is_pressed('esc'): 
        dP = 5
        PERCENT=0
        throttle()
        print('Quitting Script Now!')
        break

print('Finished! Please power down the UAV, close the interactive window, and switch to MONO_ESC_CONTROL.py to test motor function.')



# %%
