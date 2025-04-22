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

# file definition for the temp probe: reads updated temps from file every time
base_directory = '/sys/bus/w1/devices/'
dev_folder_list = glob.glob(base_directory + '28-*')

# setting up spi (serial peripheral interface) for ADC
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
adc = MCP.MCP3008(spi, cs)

# lock for thread safety: prevents threads from overwriting each other
lock = threading.Lock()

# DataFrame to store values of a and b
df = pd.DataFrame(columns=["time","a", "b", "d"])

# defining all the relay pins for high/low signals(on/off)
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

# define the pwm pins for both motors
# frequency for PWM calculated from capacitor/resistor used in low-pass circuit between Pi and motor controller
pwm_output_LHS = 12 # S/G
pwm_output_RHS = 18 # ICE
freq = 2000


##### SENSOR READING THREADS
class tempReadingThread(QThread):
    # signal object that "emits" a list object when triggered
    send_faren = pyqtSignal(list)
    # defining list of temps (3 probes)
    temps_farenheit = [0]*3

    # reading the values for each probe from the files
    def read_raw(self):
        num_files = len(dev_folder_list)
        data = []
        for i in range(num_files):
            dev_file = dev_folder_list[i] + '/w1_slave'
            with open(dev_file, 'r') as file:
                data.append(file.readlines())
        return data


    # run method is what actually gets called when the thread is started
    # this one uses an infinitie loop to keep checking the temp data
    def run(self):
        while True:
            data = self.read_raw()
            # if the first line is not YES (data read correctly), wait 0.2s and try reading again.
            # repeat until data is read correctgly
            for i in range(len(data)):
                if "YES" in data[i][0]:
                    start_index = data[i][1].find('t=') + 2
                    raw_temp = data[i][1][start_index:]
                    temp_cels = float(raw_temp) / freq      # file has temp in "millidegrees"
                    temp_far = temp_cels * (9.0/5.0) + 32.0
                    self.temps_farenheit[i] = temp_cels
                    #temps_farenheit[i] = temp_cels
                else:
                    continue
            # sending the signal with the values to the method that updates the gui
            self.send_faren.emit(self.temps_farenheit)
            time.sleep(2.5) 
    

# volt sensor reading thread
class voltReadingThread(QThread):
    new_voltage = 0.0
    # sends a float since only one value gets read
    send_volt = pyqtSignal(float)

    def run(self):
        #with lock:
            while True: 
                # have to scale the raw voltage by factor of 5 since sensor can only read up to 5v
                volt_chan = AnalogIn(adc, MCP.P2)
                new_voltage = volt_chan.voltage
                new_voltage = new_voltage*5
                self.send_volt.emit(new_voltage)
                time.sleep(.5)
    

# current reading thread
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



######### GUI INTERACTIONS 
class MOTOR_TEST_GUI(QWidget, Ui_Form):
    # INITIALIZATION METHOD
    def __init__(self):
        # calling super and initiationlization methods
        super().__init__()
        self.setupUi(self)  

        # GROUPINGS
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

        self.motor_group = QButtonGroup(self)
        self.motor_group.setExclusive(True)
        self.motor_group.addButton(self.STARTERBTN)
        self.motor_group.addButton(self.ICEBTN)

        # start with starter button checked, but nothing is on 
        self.STARTERBTN.setCheckable(True)
        self.ICEBTN.setCheckable(True)
        self.STARTERBTN.setChecked(True)
        self.ICEBTN.setChecked(False)

        # CONNECTIONS
        self.STARTGEN.sliderReleased.connect(self.dutcyc_released) # connect the slider to the pwm handler
        self.STARTGEN.valueChanged.connect(self.duty_readout_changed) # connect the slider to the readout

        # connect radio buttons to ccorresponding handler methods
        self.power_group.buttonToggled.connect(self.power_btn_change)
        self.resist_group.buttonToggled.connect(self.resist_btn_change)   

        # connect other buttons to corresponding methods
        self.RELAYSOFF.clicked.connect(self.relaysoff_clicked)
        self.RESISTORSOFF.clicked.connect(self.resistorsoff_clicked)
        self.SWITCHMOTOR.clicked.connect(self.switchmotors)
        self.ONOFF.clicked.connect(self.turningon)            
    
        # SETUP
        # starting sensor reading threads
        self.start_sensor_threads()

        #set pin numbering system to broadcom (GPIO). Using BCM since thats what PWM method needs
        GPIO.setmode(GPIO.BCM) 

        # set up pwm pins for both motors. RHS uses channel 0 and LHS uses channel 1
        GPIO.setup(pwm_output_RHS, GPIO.OUT)
        GPIO.setup(pwm_output_LHS, GPIO.OUT)
        self.pwm_sig_RHS = GPIO.PWM(pwm_output_RHS, freq)
        self.pwm_sig_LHS = GPIO.PWM(pwm_output_LHS, freq)

        # make sure all radiobuttons are disabled and all relays are off
        self.buttons_disable()
        self.all_relays_off()

        # keep track of whether turn on button has been pushed
        self.turnedon = False

        # NOTE: nothing should be on until the "turn on" button is pushed!
        return

  # SENSOR THREADS STARTING METHOD
  # creates each thread and connects it to a method to update the GUI readouts
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
        return

# READOUT UPDATE METHODS: sensors and PWM slider
    def update_temp_readout(self, temps_farenheit):
        #with lock:
            self.TEMP_1.display(temps_farenheit[0])
            self.TEMP_2.display(temps_farenheit[1])
            self.TEMP_3.display(temps_farenheit[2])
            return

    def update_volt_readout(self, new_voltage):
        # with lock: 
            self.VOLTAGE_READOUT.display(new_voltage)
            return

    def update_curr_readout(self, new_curr):
        #with lock:
            self.CURRENT_READOUT.display(new_curr)
            return


# EVENT HANDLERS
    # turn on (start)
    def turningon(self):
        motors = self.check_motor_state()
        if motors == 1:
            # sg_on method will make sure pwm for ice is off, then turn on/off appropriate relays,
            # disable the other relay buttons, and start the pwm for the sg
            self.sg_on()
        elif motors == 2:
            # ice_on method will make sure pwm for sg is off, then turn on/off appropriate relays, 
            # enable the other relay buttons, and start the pwm for the ice
            self.ice_on()

        self.turnedon = True
        self.ONOFF.setEnabled(False)

        # NOTE: could disable this until all relays off is clicked, then reenable
        return 

    # changing current duty cycle when slider is released
    def dutcyc_released(self):
        if self.turnedon == True:
            newvalue = self.STARTGEN.value()
            if self.check_motor_state() == 1: #starter, LHS
                self.pwm_sig_LHS.changeDutyCycle(newvalue)
            elif self.check_motor_state() == 2: # ice, RHS
                self.pwm_sig_RHS.changeDutyCycle(newvalue)
                
        return
    
    # updating duty cycle readout as the slider is moved
    def duty_readout_changed(self, newvalue):
        self.DUTYCYCLE_READOUT.display(newvalue)
        return

    # turning relay pins on and off as power button selection is made
    def power_btn_change(self, selected):
        if selected.isChecked() == True:
            if selected.text() == "GENERATOR TO BATTERY":
                gen2load_pin.off()
                batt2load_pin.off()
                battneg_pin.off()

                gen2batt_pin.on()

            elif selected.text() == "GENERATOR TO LOAD":
                batt2load_pin.off()
                gen2batt_pin.off()
                battneg_pin.off()
                
                gen2load_pin.on()

            elif selected.text() == "BATTERY TO LOAD":
                gen2batt_pin.off()
                gen2load_pin.off()

                batt2load_pin.on()
                battneg_pin.on()
        return
    
    # turning relay pins on and off as resistor button selection is made
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

        return


    # resistors off button: turn all resistors off
    def resistorsoff_clicked(self):
        self.all_resistors_off()
        if self.resist_group.checkedButton() is not None:
            self.resist_group.setExclusive(False)
            for button in self.resist_group.buttons():
                button.setChecked(False)
            
            self.resist_group.setExclusive(True)
        return

    # turns ALL relays off. also stops both pwm signals and resets the slider. 
    # turn_on button will have to be pressed again to turn the pwm signals back on
    def relaysoff_clicked(self):
        # turn all the relays off and reset the slider. slider method will turn pwm signals off
        self.all_relays_off()
        self.slider_reset()
        self.turnedon = False
        self.ONOFF.setEnabled(True)

        # turn resistor group off
        if self.resist_group.checkedButton() is not None:
            self.resist_group.setExclusive(False)
            for button in self.resist_group.buttons():
                button.setChecked(False)
            self.resist_group.setExclusive(True)

        # turn off power group
        if self.power_group.checkedButton() is not None:
            self.power_group.setExclusive(False)
            for button in self.power_group.buttons():
                button.setChecked(False)
            self.power_group.setExclusive(True)  
        return     

    def slider_reset(self):
        # turn both pwm signals off (doesn't matter which is on)
        self.pwm_sig_LHS.stop()
        self.pwm_sig_RHS.stop()

        # reset the slider and the readout
        # temp block signals from slider while setting value so that dutcycle_released() method isn't called
        self.STARTGEN.blockSignals(True)
        self.STARTGEN.setValue(0)
        self.STARTGEN.blockSignals(False)
        self.DUTYCYCLE_READOUT.display(0)
        return 

    def switchmotors(self):
        motor_state = self.motor_group.checkedButton()
        if motor_state == self.STARTERBTN:
            self.ICEBTN.setChecked(True)
            if self.turnedon == True:
                self.ice_on()
        else:
            self.STARTERBTN.setChecked(True)
            if self.turnedon == True:
                self.sg_on()

        return

# OTHER METHODS
    # disable all GUI radio buttons (used when s/g is on)
    def buttons_disable(self):
        for button in self.power_group.buttons():
            button.setEnabled(False)
        
        for button in self.resist_group.buttons():
            button.setEnabled(False)

    # enables all GUI radio buttons (used when ice is on)
    def buttons_enable(self):
        for button in self.power_group.buttons():
            button.setEnabled(True)

        for button in self.resist_group.buttons():
            button.setEnabled(True)

    # turn off the pin signals for all resistor relays
    def all_resistors_off(self):
        r7_pin.off()
        r6_pin.off()
        r5_pin.off()
        r4_pin.off()
        r3_pin.off()
        r2_pin.off()
        r1_pin.off()
        return

    # turn off the pin signals for ALL relays
    def all_relays_off(self):
        r7_pin.off()
        r6_pin.off()
        r5_pin.off()
        r4_pin.off()
        r3_pin.off()
        r2_pin.off()
        r1_pin.off()

        batt2load_pin.off()
        gen2load_pin.off()
        gen2batt_pin.off()
        pwr2MC_pin.off()
        SGcontrol_pin.off()
        battneg_pin.off()
        return
    
    # check the state of the motor ubttons: returns 1 for S/G (LHS) and 2 for ICE (RHS)
    def check_motor_state(self):
        checked = self.motor_group.checkedButton()
        if checked == self.STARTERBTN:
            return 1
        elif checked == self.ICEBTN:
            return 2
        
    # turn on the s/g motor
    def sg_on(self):
        # if pwm signal for other motor was on, stop it
        self.pwm_output_RHS.stop()

        # turn off all relays, then turn on just the sg pin
        self.all_relays_off()
        SGcontrol_pin.on()

        # start the sg motor pwm signal
        self.pwm_output_LHS.start(0)

        # disable the other relay buttons
        self.buttons_disable()
        return
    
    def ice_on(self):
        # if pwm signal for other motor was on, stop it
        self.pwm_output_LHS.stop()
        SGcontrol_pin.off()

        # turn on the 48v to MC pin and the pwm signal 
        pwr2MC_pin.on()
        self.pwm_output_RHS.start(0)

        # turn on the other relay buttons
        self.buttons_enable()
        return



# RUNNING APP
app = QApplication(sys.argv)
window = MOTOR_TEST_GUI()
window.show()
sys.exit(app.exec())
