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

batt2load_pin = LED(0)
gen2load_pin = LED(5)
gen2batt_pin = LED(6)
pwr2MC_pin = LED(16)
SGcontrol_pin = LED(20)
battneg_pin = LED(21)
r7_pin = LED(17)
r6_pin = LED(27)
r5_pin = LED(22)
r4_pin = LED(14)
r3_pin = LED(15)
r2_pin = LED(23)
r1_pin = LED(24)

pwm_output_pin = 100



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

        # starter with sg control pin on
        SGcontrol_pin.on()
        pwm_output_pin = 19 # GPIO 19 for LHS motor
        GPIO.setmode(GPIO.BCM) #set pin numbering system to broadcom (GPIO)
        GPIO.setup(pwm_output_pin,GPIO.OUT)
        self.pwm_sig = GPIO.PWM(pwm_output_pin,1000)	# creating a PWM object: GPIO.PWM(pin no, frequency)
        self.pwm_sig.start(0)

        # groupings
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

        self.STARTERBTN.setCheckable(True)
        self.STARTERBTN.setChecked(True)


        # connections
        self.STARTGEN.valueChanged.connect(self.dutcyc_changed)
        self.GEN2BATT.toggled.connect(lambda:self.power_btn_change(self.GEN2BATT))
        self.GEN2LOAD.toggled.connect(lambda:self.power_btn_change(self.GEN2LOAD))
        self.BATT2LOAD.toggled.connect(lambda:self.power_btn_change(self.BATT2LOAD))
        self.STARTERBTN.toggled.connect(lambda:self.starter_btn_change(self.STARTERBTN))

        self.R7.toggled.connect(lambda:self.resist_btn_change(self.R7))
        self.R6.toggled.connect(lambda:self.resist_btn_change(self.R6))
        self.R5.toggled.connect(lambda:self.resist_btn_change(self.R5))
        self.R4.toggled.connect(lambda:self.resist_btn_change(self.R4))
        self.R3.toggled.connect(lambda:self.resist_btn_change(self.R3))
        self.R2.toggled.connect(lambda:self.resist_btn_change(self.R2))
        self.R1.toggled.connect(lambda:self.resist_btn_change(self.R1))        
    
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
    def dutcyc_changed(self, newvalue):
        self.DUTYCYCLE_READOUT.display(newvalue)
        self.pwm_sig.ChangeDutyCycle(newvalue)


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
                gen2load_pin.off()
                batt2load_pin.off()

                gen2batt_pin.on()

            elif selected.text() == "GENERATOR TO LOAD":
                batt2load_pin.off()
                gen2batt_pin.off()
                
                gen2load_pin.on()

            elif selected.text() == "BATTERY TO LOAD":
                gen2batt_pin.off()
                gen2load_pin.off()

                batt2load_pin.on()


    def starter_btn_change(self, starterbtn):
        if starterbtn.isChecked() == True:
            SGcontrol_pin.on()
            self.STARTERLBL.setText("STARTER ON")
            pwm_output_pin = 19 # GPIO 19 for LHS MOTOR

            GPIO.setup(pwm_output_pin,GPIO.OUT)
            self.pwm_sig = GPIO.PWM(pwm_output_pin,1000)	# creating a PWM object: GPIO.PWM(pin no, frequency)
            self.pwm_sig.start(0)

        else:
            SGcontrol_pin.off()
            self.STARTERLBL.setText("STARTER OFF")
            pwm_output_pin = 18 # GPIO 18 for RHS MOTOR

            GPIO.setup(pwm_output_pin,GPIO.OUT)
            self.pwm_sig = GPIO.PWM(pwm_output_pin,1000)	# creating a PWM object: GPIO.PWM(pin no, frequency)
            self.pwm_sig.start(0)

    
    def resist_btn_change(self, selected):
        if selected.isChecked() == True:
            if selected.text() == "Resistor 7 (HIGH)":
                self.all_resistors_off()
                r7_pin.on()

            elif selected.text() == "Resistor 6":
                self.all_resistors_off()
                r6_pin.on()

            elif selected.text() == "Resistor 5":
                self.all_resistors_off()
                r5_pin.on()

            elif selected.text() == "Resistor 4":
                self.all_resistors_off()
                r4_pin.on()

            elif selected.text() == "Resistor 3":
                self.all_resistors_off()
                r3_pin.on()

            elif selected.text() == "Resistor 2":
                self.all_resistors_off()
                r2_pin.on()

            elif selected.text() == "Resistor 1 (LOW)":
                self.all_resistors_off()
                r1_pin.on()
            
            
    def all_resistors_off(self):
        r7_pin.off()
        r6_pin.off()
        r5_pin.off()
        r4_pin.off()
        r3_pin.off()
        r2_pin.off()
        r1_pin.off()
        return




# RUNNING APP
app = QApplication(sys.argv)
window = MOTOR_TEST_GUI()
window.show()
sys.exit(app.exec())
