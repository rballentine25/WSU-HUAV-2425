import sys
from PyQt6.QtWidgets import QApplication, QWidget, QButtonGroup
from PyQt6.QtCore import QTimer
from MOTOR_TEST_GUI_UIDEF import Ui_Form  
import glob
import time

# file definition for the temp probe
base_directory = '/sys/bus/w1/devices/'
dev_folder = glob.glob(base_directory + '28-*')[0]  
dev_file = dev_folder + '/w1_slave'

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
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_temp_readout)
        self.timer.start(200)



    def read_raw(self):
        file = open(dev_file, 'r')
        data = file.readlines()
        file.close()
        return data


    def read_temp(self):
        data = self.read_raw()
        
        # if the first line is not YES (data read correctly), wait 0.2s and try reading again.
        # repeat until data is read correctgly
        while "YES" not in data[0]:
            time.sleep(0.2)
            data = self.read_raw()    
        
        # if data is read correctly, look for the t= in the file for the start index, then read 
        # in the rest of the following string (file ends with the temp)
        start_index = data[1].find('t=') + 2
        raw_temp = data[1][start_index:]
        temp_cels = float(raw_temp) / 1000      # file has temp in "millidegrees"
        temp_far = temp_cels * (9.0/5.0) + 32.0
        return temp_far



# EVENT HANDLERS
    def update_sg_readout(self, newvalue):
        self.STARTGEN_READOUT.display(newvalue)

    def update_ice_readout(self, newvalue):
        self.ICE_READOUT.display(newvalue)

    def update_temp_readout(self):
        newtemp = self.read_temp()
        self.TEMP_READOUT.display(newtemp)
        


# RUNNING APP
app = QApplication(sys.argv)
window = MOTOR_TEST_GUI()
window.show()
sys.exit(app.exec())
