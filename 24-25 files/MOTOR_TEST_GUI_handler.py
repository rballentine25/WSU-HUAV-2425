import sys
from PyQt6.QtWidgets import QApplication, QWidget, QButtonGroup
from PyQt6.QtCore import QTimer, QEvent, QCoreApplication
from MOTOR_TEST_GUI_UIDEF import Ui_Form  
import glob
import time
from time import sleep
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# file definition for the temp probe
base_directory = '/sys/bus/w1/devices/'
dev_folder_list = glob.glob(base_directory + '28-*')
temps_farenheit = [0]*3

# setting up spi for ADC
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
adc = MCP.MCP3008(spi, cs)

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

        # connections
        self.STARTGEN.valueChanged.connect(self.update_sg_readout)
        self.ICEEMULATOR.valueChanged.connect(self.update_ice_readout)
        # TEST: self.STARTGEN.valueChanged.connect(self.update_temp_readout)

        # timer
        self.timer1 = QTimer(self)
        self.timer2 = QTimer(self)
        self.timer1.timeout.connect(self.update_temp_readout)
        self.timer2.timeout.connect(self.update_volt_readout)
        self.timer2.start(300)
        self.timer1.start(500)



    def read_raw(self):
        num_files = len(dev_folder_list)
        data = []
        for i in range(num_files):
            dev_file = dev_folder_list[i] + '/w1_slave'
            with open(dev_file, 'r') as file:
                data.append(file.readlines())
            
        return data


    def read_temp(self):
        data = self.read_raw()
        # if the first line is not YES (data read correctly), wait 0.2s and try reading again.
        # repeat until data is read correctgly
        for i in range(len(data)):
            if "YES" in data[i][0]:
                start_index = data[i][1].find('t=') + 2
                raw_temp = data[i][1][start_index:]
                temp_cels = float(raw_temp) / 1000      # file has temp in "millidegrees"
                temp_far = temp_cels * (9.0/5.0) + 32.0
                temps_farenheit[i] = temp_far
            else:
                 continue
        
        return temps_farenheit      



# EVENT HANDLERS
    def update_sg_readout(self, newvalue):
        self.STARTGEN_READOUT.display(newvalue)

    def update_ice_readout(self, newvalue):
        self.ICE_READOUT.display(newvalue)

    def update_temp_readout(self):
        # start = time.time()
        newtemp = self.read_temp()
        self.TEMP_1.display(newtemp[0])
        self.TEMP_2.display(newtemp[1])
        self.TEMP_3.display(newtemp[2])
        # end = time.time()
        # print(end-start)

    def update_volt_readout(self):
        curr_chan = AnalogIn(adc, MCP.P2)
        new_voltage = curr_chan.voltage
        self.VOLTAGE_READOUT.display(new_voltage)




# RUNNING APP
app = QApplication(sys.argv)
window = MOTOR_TEST_GUI()
window.show()
sys.exit(app.exec())
