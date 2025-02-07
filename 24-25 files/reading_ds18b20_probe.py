import glob # glob is a pattern match library for importing files
import time


# finding the file with temp data: glob.glob() returns a list of files/folders that 
# match the input pattern. * is a wildcard. dev_folder arg returns the first entry 
# in the list that matches the device pattern. data is in the file w1_slave within the 
# device folder
base_directory = '/sys/bus/w1/devices/'
dev_folder = glob.glob(base_directory + '28-*')[0]  
dev_file = dev_folder + '/w1_slave'

def read_raw():
    file = open(dev_file, 'r')
    data = file.readlines()
    file.close()
    return data


def read_temp():
    data = read_raw()
    
    # if the first line is not YES (data read correctly), wait 0.2s and try reading again.
    # repeat until data is read correctgly
    while "YES" not in data[0]:
        time.sleep(0.2)
        data = read_raw()    
    
    # if data is read correctly, look for the t= in the file for the start index, then read 
    # in the rest of the following string (file ends with the temp)
    start_index = data[1].find('t=') + 2
    raw_temp = data[1][start_index:]
    temp_cels = float(raw_temp) / 1000      # file has temp in "millidegrees"
    temp_far = temp_cels * (9.0/5.0) + 32.0
    return [temp_far]

for i in range(20):
    print(read_temp())
    time.sleep(0.2)