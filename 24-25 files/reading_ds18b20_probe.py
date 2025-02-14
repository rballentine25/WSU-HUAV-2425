import glob # glob is a pattern match library for importing files
import time
from time import sleep


# finding the file with temp data: glob.glob() returns a list of files/folders that 
# match the input pattern. * is a wildcard. dev_folder arg returns the first entry 
# in the list that matches the device pattern. data is in the file w1_slave within the 
# device folder
base_directory = '/sys/bus/w1/devices/'
dev_folder_list = glob.glob(base_directory + '28-*')
temps_farenheit = [0]*3

def read_raw():
    num_files = len(dev_folder_list)
    data = []
    for i in range(num_files):
            dev_file = dev_folder_list[i] + '/w1_slave'
            file = open(dev_file, 'r')
            data.append(file.readlines())
            file.close()
    return data


def read_temp():
        data = read_raw()
        # if the first line is not YES (data read correctly), wait 0.2s and try reading again.
        # repeat until data is read correctgly
        for i in range(len(data)):
            if "YES" not in data[i][0]:
                continue
            else:
                start_index = data[i][1].find('t=') + 2
                raw_temp = data[i][1][start_index:]
                temp_cels = float(raw_temp) / 1000      # file has temp in "millidegrees"
                temp_far = temp_cels * (9.0/5.0) + 32.0
                temps_farenheit[i] = temp_far
        
        return temps_farenheit

start = time.time()
temps = read_temp()
end = time.time()
print("time to execute: ", (end-start), " sec")

# for j in range(50):
#     print("TEMPS AT CYCLE ", j, "\n")
#     temps = read_temp()
#     for i in range(3):
#         print(temps[i])
#     sleep(0.3)