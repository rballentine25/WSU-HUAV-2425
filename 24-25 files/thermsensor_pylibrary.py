from w1thermsensor import W1ThermSensor, Sensor
import time
import glob

base_directory = '/sys/bus/w1/devices/'
dev_folder_list = glob.glob(base_directory + '28-*')
num_files = len(dev_folder_list)
sensor_ids = []

for device in dev_folder_list:
    splitbyslash = device.split('/')
    curr_id = splitbyslash[-1] # get the last one, which shuold eb the name
    sensor_ids.append(curr_id[3:]) # w1thermsensor wants the id w/o "28-" at beginning

print(sensor_ids)

# making sure we're reading all the sensors correctly
# sensor_list = W1ThermSensor.get_available_sensors()
# print(sensor_list)

sensor1 = W1ThermSensor(sensor_id = sensor_ids[0])
sensor2 = W1ThermSensor(sensor_id = sensor_ids[1])
sensor3 = W1ThermSensor(sensor_id = sensor_ids[2])


def read_temp(sensor): 
    temp_c = sensor.get_temperature()
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_c, temp_f

n = 0
sensor0 = W1ThermSensor()
while True:
    # if n > 5:
    #     break

    #start = time.time()
    temp_c, temp_f = read_temp(sensor1)
    print(f"Temperature for S1: {temp_c:.2f}°C / {temp_f:.2f}°F")
    #end1 = time.time()
    
    temp_c, temp_f = read_temp(sensor2)
    print(f"Temperature for S2: {temp_c:.2f}°C / {temp_f:.2f}°F")

    temp_c, temp_f = read_temp(sensor3)
    print(f"Temperature for S3: {temp_c:.2f}°C / {temp_f:.2f}°F")
    #end2 = time.time()
    
    #print("Time for one reading: ", (end1-start), " TIme for all readuings: ", (end2-start))
    print("\n")

    n+=1
    #time.sleep(.1)