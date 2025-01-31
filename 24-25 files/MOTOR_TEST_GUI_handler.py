import sys
from PyQt6.QtWidgets import QApplication, QWidget, QButtonGroup
from MOTOR_TEST_GUI_UIDEF import Ui_Form  

class MOTOR_TEST_GUI(QWidget, Ui_Form):
    # INITIALIZATION METHOD
    def __init__(self):
        super().__init__()
        self.setupUi(self)  

        # groupings
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.LOUD)
        self.mode_group.addButton(self.QUIET)
        self.QUIET.setChecked(True)

        # connections
        self.STARTGEN.valueChanged.connect(self.update_sg_readout)
        self.ICEEMULATOR.valueChanged.connect(self.update_ice_readout)
        # TEST: self.STARTGEN.valueChanged.connect(self.update_temp_readout)


    # READING SIGNALS 
    def read_temp(self):
        #stuff here (READING FROM ADC)
        newtemp = 4.667
        return newtemp


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
