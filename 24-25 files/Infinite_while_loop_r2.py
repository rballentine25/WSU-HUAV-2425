# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:22:29 2025

@author: Lincoln DeHaven
"""

import datetime
import threading
import time
import pandas as pd
import os
import glob

# Global variables
a = 0
b = 0
temp_c = 0
c = 0  # Tracker variable for row index

# Load 1-Wire modules (if not already loaded)
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Get the device folder (should start with "28-")
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]  # Get first detected sensor
device_file = device_folder + '/w1_slave'

# Lock for thread safety
lock = threading.Lock()

# DataFrame to store values of a and b
df = pd.DataFrame(columns=["time","a", "b", "d"])

def read_temp_raw():
    """Reads raw temperature data from sensor."""
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temp():
    global temp_c
    """Parses temperature from raw sensor data."""
    lines = read_temp_raw()
    
    # Retry if CRC check fails
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    
    # Extract temperature value
    temp_output = lines[1].split("t=")
    if len(temp_output) > 1:
        temp_c = float(temp_output[1]) / 1000.0  # Convert to Celsius
        temp_f = temp_c * 9.0 / 5.0 + 32.0       # Convert to Fahrenheit
        return temp_c, temp_f

# Read and print temperature every second

def temperature():
    global temp_c
    while True:
        with lock:  
            temp_c, temp_f = read_temp()
            print(f"Temperature: {temp_c:.2f}°C / {temp_f:.2f}°F")
            time.sleep(1)

def print_cube(num):
    global a
    while a < 61:
        with lock:  # Ensures that only one thread can modify 'a' at a time
            a += 1
        print("Cube: {}".format(num * num * num))
        time.sleep(5)
        

def print_square(num):
    global b
    while b < 31:
        with lock:  # Ensures that only one thread can modify 'b' at a time
            b += 1
        print("Square: {}".format(num * num))
        time.sleep(10)
        
def tracker():
    global a
    global b
    global c
    global df
    global temp_c
    while a <= 60 or b <= 30:
        with lock:  # Ensure reading the values of a and b in a thread-safe way
            # Check if the current row index 'c' exists in the DataFrame
            if c >= len(df):
                # Append a new row if 'c' is out of bounds
                df.loc[c] = [datetime.datetime.now(), a, b, temp_c]
            else:
                # Update the existing row with the current values of 'a' and 'b'
                df.loc[c, "time"] = datetime.datetime.now()
                df.loc[c, "a"] = a
                df.loc[c, "b"] = b
                df.loc[c, "d"] = temp_c
            # Update the tracker variable 'c' for the next row
            c += 1
        

if __name__ == "__main__":
    # Create two threads for printing square and cube
    t1 = threading.Thread(target=print_square, args=(10,))
    t2 = threading.Thread(target=print_cube, args=(10,))
    t3 = threading.Thread(target=temperature)
    t4 = threading.Thread(target=tracker)

    # Start all threads
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    
    t1.join()
    t2.join()
    t3.join()
    t4.join()

    # Wait for threads to finish

    # Print the DataFrame after all threads have finished
    print(df)
    print("Done!")
