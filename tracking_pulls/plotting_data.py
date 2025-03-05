import matplotlib.pyplot as plt
import matplotlib as mplt
import numpy as np
import h5py as hp
import copy

def derivative(xvalue, yvalue):
    ydiff = np.array(yvalue[1:]) - np.array(yvalue[:-1])
    xdiff = np.array(xvalue[1:]) - np.array(xvalue[:-1])
    return ydiff/xdiff

if __name__ == '__main__':
    fig, ax = plt.subplots(2,1)
    with hp.File('./recorded_data.hdf5', 'r') as hfile:
        grp = hfile['18-2-2025']['17:0001-01-01 00:00:00:59']
        data = copy.deepcopy(np.array(grp['wdata']))
    dt = 0.1
    time = np.arange(0, len(data)*dt, dt)
    slope = derivative(time, data)
    second_derivative = derivative(time[:-1], slope)
    max_force_gen = max(slope)
    min_force_gen = min(slope)
    max_index = np.argmax(slope)
    min_index = np.argmin(slope)
    ax[0].plot(time, data)
    ax[0].fill_between(time[max_index:min_index], data[max_index:min_index], alpha=0.5)
    ax[1].plot(time[:-1], slope, label='1st Derivative')
    ax[1].plot(time[1:-1], second_derivative, label='2nd Derivative')
    plt.show()
