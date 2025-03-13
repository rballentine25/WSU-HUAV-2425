import time
import glob
from w1thermsensor import W1ThermSensor
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import pandas as pd

# setting up temp probes
base_directory = '/sys/bus/w1/devices/'
dev_folder_list = glob.glob(base_directory + '28-*')
num_files = len(dev_folder_list)
sensors = []
for device in dev_folder_list:
    splitbyslash = device.split('/')
    curr_id = splitbyslash[-1] # get the last one, which shuold eb the name
    sensors.append(W1ThermSensor(sensor_id = curr_id[3:])) # w1thermsensor wants the id w/o "28-" at beginning

# setting up spi comm for ADC
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
adc = MCP.MCP3008(spi, cs)

# lock for thread safety: prevents threads from overwriting each other
lock = threading.Lock()