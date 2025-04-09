import sys
from PyQt6.QtWidgets import QApplication, QWidget, QButtonGroup
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from MOTOR_TEST_GUI_UIDEF import Ui_Form  
import glob
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import pandas as pd
import time
import RPi.GPIO as GPIO
from gpiozero import LED, PWMLED

# file definition for the temp probe
base_directory = '/sys/bus/w1/devices/'
dev_folder_list = glob.glob(base_directory + '28-*')

# setting up spi for ADC
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
adc = MCP.MCP3008(spi, cs)

# lock for thread safety: prevents threads from overwriting each other
lock = threading.Lock()

# DataFrame to store values of a and b
df = pd.DataFrame(columns=["time","a", "b", "d"])

# new_voltage = 0.0
# temps_farenheit = [0]*3

class tempReadingThread(QThread):
    send_faren = pyqtSignal(list)
    temps_farenheit = [0]*3

    def read_raw(self):
        num_files = len(dev_folder_list)
        data = []
        for i in range(num_files):
            dev_file = dev_folder_list[i] + '/w1_slave'
            with open(dev_file, 'r') as file:
                data.append(file.readlines())
        return data


    def run(self):
        #with lock:
            while True:
                data = self.read_raw()
                # if the first line is not YES (data read correctly), wait 0.2s and try reading again.
                # repeat until data is read correctgly
                for i in range(len(data)):
                    if "YES" in data[i][0]:
                        start_index = data[i][1].find('t=') + 2
                        raw_temp = data[i][1][start_index:]
                        temp_cels = float(raw_temp) / 1000      # file has temp in "millidegrees"
                        temp_far = temp_cels * (9.0/5.0) + 32.0
                        self.temps_farenheit[i] = temp_cels
                        #temps_farenheit[i] = temp_cels
                    else:
                        continue
                    
                self.send_faren.emit(self.temps_farenheit)
                time.sleep(2.5) 
    

class voltReadingThread(QThread):
    new_voltage = 0.0
    send_volt = pyqtSignal(float)

    def run(self):
        #with lock:
            while True: 
                volt_chan = AnalogIn(adc, MCP.P2)
                new_voltage = volt_chan.voltage
                new_voltage = new_voltage*5
                self.send_volt.emit(new_voltage)
                time.sleep(.5)


class currReadingThread(QThread):
    new_curr = 0.0
    send_curr = pyqtSignal(float)

    def run(self):
        #with lock:
            while True: 
                curr_chan = AnalogIn(adc, MCP.P0)
                # supposed to be converting: 1mv/10ma
                new_curr_pre = curr_chan.voltage 
                # TODO: adjustby sensor specsheet 
                new_curr = new_curr_pre * 5 * 10
                self.send_curr.emit(new_curr)
                time.sleep(.5)


class MOTOR_TEST_GUI(QWidget, Ui_Form):
    # INITIALIZATION METHOD
    def __init__(self):
        super().__init__()
        self.setupUi(self)  

        # groupings
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.GEN)
        self.mode_group.addButton(self.STARTER)
        self.STARTER.setChecked(True)

        self.power_group = QButtonGroup(self)
        self.power_group.addButton(self.GEN2BATT)
        self.power_group.addButton(self.GEN2LOAD)
        self.power_group.addButton(self.BATT2LOAD)

        self.resist_group = QButtonGroup(self)
        self.resist_group.addButton(self.R1)
        self.resist_group.addButton(self.R2)
        self.resist_group.addButton(self.R3)
        self.resist_group.addButton(self.R4)
        self.resist_group.addButton(self.R5)
        self.resist_group.addButton(self.R6)
        self.resist_group.addButton(self.R7)

        # connections
        self.STARTGEN.valueChanged.connect(self.update_dutcyc_readout)
        self.GEN2BATT.toggled.connect(lambda:self.power_btn_change(self.GEN2BATT))
        self.GEN2LOAD.toggled.connect(lambda:self.power_btn_change(self.GEN2LOAD))
        self.BATT2LOAD.toggled.connect(lambda:self.power_btn_change(self.BATT2LOAD))
        
    
        # TEST: self.STARTGEN.valueChanged.connect(self.update_temp_readout)

        # # timer
        # self.timer1 = QTimer(self)
        # self.timer2 = QTimer(self)
        # self.timer1.timeout.connect(self.update_temp_readout)
        # self.timer2.timeout.connect(self.update_volt_readout)
        # self.timer2.timeout.connect(self.update_curr_readout)
        # self.timer2.start(300)
        # self.timer1.start(500)

        # temp_thread = threading.Thread(target=self.update_temp_readout)
        # temp_thread.start()
        # temp_thread.join()

        # volt_thread = threading.Thread(target=self.update_volt_readout)
        # volt_thread.start()
        # volt_thread.join()
        self.start_sensor_threads()
  

    def start_sensor_threads(self):
        self.temp_thread = tempReadingThread()
        self.volt_thread = voltReadingThread()
        self.curr_thread = currReadingThread()

        self.temp_thread.send_faren.connect(self.update_temp_readout)
        self.volt_thread.send_volt.connect(self.update_volt_readout)
        self.curr_thread.send_curr.connect(self.update_curr_readout)
        
        self.temp_thread.start()
        self.volt_thread.start()
        self.curr_thread.start()

# EVENT HANDLERS
    def update_dutcyc_readout(self, newvalue):
        self.DUTYCYCLE_READOUT.display(newvalue)

    def update_temp_readout(self, temps_farenheit):
        #with lock:
            self.TEMP_1.display(temps_farenheit[0])
            self.TEMP_2.display(temps_farenheit[1])
            self.TEMP_3.display(temps_farenheit[2])

    def update_volt_readout(self, new_voltage):
        # with lock: 
            self.VOLTAGE_READOUT.display(new_voltage)

    def update_curr_readout(self, new_curr):
        #with lock:
            self.CURRENT_READOUT.display(new_curr)

    def power_btn_change(self, selected):
        if selected.isChecked() == True:
            if selected.text() == "GENERATOR TO BATTERY":
                print("GEN2BATT selected")

            elif selected.text() == "GENERATOR TO LOAD":
                print("GEN2LOAD selected")

            elif selected.text() == "BATTERY TO LOAD":
                print("BATT2LOAD selected")



# RUNNING APP
app = QApplication(sys.argv)
window = MOTOR_TEST_GUI()
window.show()
sys.exit(app.exec())
