import os
import glob
import time

# Load 1-Wire modules (if not already loaded)
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Get the device folder (should start with "28-")
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]  # Get first detected sensor
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    """Reads raw temperature data from sensor."""
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temp():
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
while True:
    temp_c, temp_f = read_temp()
    print(f"Temperature: {temp_c:.2f}°C / {temp_f:.2f}°F")
    time.sleep(1)
