#%% Import packages and data
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
import math as mt

#data = pd.read_csv(r'C:\Users\Lucas Duncan\Documents\Python Scripts\DATA\hybrid_uav\Cell_1_Calibration.csv', skiprows=1).to_numpy()
data = pd.read_csv(r'C:\Users\Lucas Duncan\Downloads\Load_Cell_2_Increment_5.csv', skiprows=1).to_numpy()
t = data[:,0]
x = data[:,1]

# %matplotlib qt
# plt.plot(t, x, 'r-', label='Raw Force Data')
# plt.title('Raw Thrust vs. Time')
# plt.xlabel('Time (s)')
# plt.ylabel('Thrust (lbf)')
# plt.legend()
# plt.show()

#%% Get stats on noisy data
# plt.close()
# start = 40
# stop = 50
# idxs = np.where((t>start) & (t<stop))
# t_stat = t[idxs]
# x_stat = x[idxs]*(10**3)
# hist  = plt.hist(x_stat, bins=1000)
# plt.title('Histogram of Load Cell Voltage Readings During Constant Applied Load of 0.677 lb')
# plt.xlabel('Voltage Reading (mV)')
# plt.ylabel('Frequency')
# plt.grid()

# stddev = np.std(x_stat)
# var = stddev**2
# range = np.max(x_stat) - np.min(x_stat)
# print('Standard Deviation: ', stddev)
# print('Variance: ', var)
# print('Range: ', range)



#%% Use lowpass filter on data
fs = 1/np.average(np.diff(t))
cutoff = 1
nyq = 0.5 * fs
order = 2
n = len(t)

def butter_lowpass_filter(data, cutoff, nyq, order):
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.filtfilt(b, a, data)
    return y

smooth_x = butter_lowpass_filter(x, cutoff, nyq, order)

# Get Peaks
peaks = signal.argrelextrema(smooth_x, np.greater)

peak_ts = t[peaks]
peak_xs = smooth_x[peaks]

# Plots!
plt.plot(t, x, c='r', label='Raw Force Data')
plt.plot(t,smooth_x,'b-', label='Frequency Filtered Data')
# plt.scatter(peak_ts, peak_xs, c='g', label='Peaks')
plt.xlabel('Time (s)')
plt.ylabel('Thrust (lbf)')
plt.legend(loc='upper left')
plt.grid()
plt.minorticks_on()
plt.title('Load Cell #2 Thrust vs Time')
plt.show()


# %% Get and plot average force value over a time interval
t_start = 40 # seconds, measured from start of dataset
t_stop = 48

t_range = np.where((t>t_start) & (t<t_stop))[0]
tt = t[t_range]
xx = smooth_x[t_range]
avg_xx = np.average(xx)
print(avg_xx)
plt.plot(tt, xx, 'b-', label='smooth force')
plt.plot(tt, avg_xx*np.ones(len(tt)), 'g--', label='avg force')
plt.legend()



# %% Linear Calibration (Outdated)
# V0 = 0.0004256068388790014
# V1 = 0.0008304115862871551
# V2 = 0.0011682926898153893
# V3 = 0.001530867227837291

# F0 = 9.81 * 0
# F1 = 9.81 * 0.166
# F2 = 9.81 * 0.307
# F3 = 9.81 * 0.441

# volts = [V0, V1, V2, V3]
# load = [F0, F1, F2, F3]

# m, b = np.polyfit(volts, load, deg=1)

# print('Load-Offset: ', b)
# print('Newtons Per Volt: ', m)
# plt.plot(volts, load, 'o')
# v_fit = np.linspace(0, 0.0022, 10)
# f_fit = v_fit*m + b
# plt.plot(v_fit, f_fit)
# plt.title('Force vs Average Voltage')
# plt.xlabel('Average Dewesoft Voltage (V)')
# plt.ylabel('Thrust Force (N)')
# plt.grid()
# %%
