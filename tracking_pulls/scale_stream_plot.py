import time
import datetime
import h5py as hp

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mplt
import matplotlib.animation as anim
from scipy.ndimage import shift

import serial
import serial.tools.list_ports

class Scale:
    def __init__(self, ax, tlim, dt=0.1, debug=False):
        self.port = None
        self.arduino = None
        self.dt = dt
        self.ax = ax
        self.tlim = tlim
        self.tend = tlim
        self.maxw = 3
        self.tdata = [0]
        self.wdata = [0]
        self.line = mplt.lines.Line2D(self.tdata, self.wdata)
        self.ax.add_line(self.line)
        self.xlow = 0
        self.xhigh = tlim
        self.ax.set_xlim(self.xlow, self.xhigh)
        self.ax.set_ylim(-1, self.maxw)
        self.debug = debug
        
        self.HANDSHAKE = 0
        self.VOLTAGE_REQUEST = 1
        self.ON_REQUEST = 2
        self.STREAM = 3
        self.READ_DAQ_DELAY = 4
        self.TARE = 5

        self.ax.set_xlabel('time (s)')
        self.ax.set_ylabel('Weight (kg)')

    def set_arduino(self, arduino):
        self.arduino = arduino

    def set_lims(self, xlims, ylims):
        self.ax.set_xlim(xlims[0], xlims[1])
        self.ax.set_ylim(ylims[0], ylims[1])
        
    def update(self, y):
        lastt = self.tdata[-1]
        if lastt >= self.tend: 
            self.tend += self.tlim
            self.ax.set_xlim(0, self.tend)            
            self.ax.figure.canvas.draw()

        if y > self.maxw:
            self.maxw = y
            self.ax.set_ylim(-1, self.maxw + 1)
            self.ax.figure.canvas.draw()
        # This slightly more complex calculation avoids floating-point issues
        # from just repeatedly adding `self.dt` to the previous value.
        t = self.tdata[0] + len(self.tdata) * self.dt

        self.tdata.append(t)
        self.wdata.append(y)
        self.line.set_data(self.tdata, self.wdata)
        return self.line, 


    def find_arduino(self):
        '''Get the name of the port that is connected to Arduino.'''
        if self.port is None:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if p.manufacturer is not None and "Arduino" in p.manufacturer:
                    port = p.device
        self.port = port
        return port

    def tare(self):
        self.arduino.close()
        self.arduino.open()

        time.sleep(1)
        _ = self.arduino.read_all()

        self.arduino.write(bytes([self.TARE]))
        
    
    def handshake_arduino(self, sleep_time=1, print_handshake_message=False):
        '''Make sure connection is established by sending
        and receiving bytes.'''
        # Close and reopen
        self.arduino.close()
        self.arduino.open()

        # Chill out while everything gets set
        time.sleep(sleep_time)

        # Set a long timeout to complete handshake
        timeout = self.arduino.timeout
        self.arduino.timeout = 2

        # Read and discard everything that may be in the input buffer
        _ = self.arduino.read_all()

        # Send request to Arduino
        self.arduino.write(bytes([self.HANDSHAKE]))

        # Read in what Arduino sent
        handshake_message = self.arduino.read_until()

        # Send and receive request again
        self.arduino.write(bytes([self.HANDSHAKE]))
        handshake_message = self.arduino.read_until()

        # Print the handshake message, if desired
        if print_handshake_message:
            print("Handshake message: " + handshake_message.decode())

        # Reset the timeout
        self.arduino.timeout = timeout
        return 1

    def parse_raw(self, raw):
        '''Parse bytes output from Arduino.'''
        raw = raw.decode()
        if raw[-1] != "\n":
            raise ValueError(
                "Input must end with newline, otherwise message is incomplete."
            )

        t, W = raw.rstrip().split(",")
        return int(t), float(W) 

    def daq_read(self, n_data=1, delay=100):
        '''Obtain `n_data` data points from an Arduino stream
        with a delay of `delay` milliseconds between each.'''
        # Specify delay
        self.arduino.write(bytes([self.READ_DAQ_DELAY]) + (str(delay) + "x").encode())

        # Initialize output
        time_ms = np.empty(n_data)
        weight = np.empty(n_data)

        # Turn on the stream
        self.arduino.write(bytes([self.STREAM]))

        # Receive data
        i = 0
        while i < n_data:
            raw = self.arduino.read_until()
            try:
                t, W = self.parse_raw(raw)
                time_ms[i] = t
                weight[i] = W
                i += 1
            except:
                pass

        # Turn off the stream
        self.arduino.write(bytes([ON_REQUEST]))

        return time_ms, weight

    def daq_stream(self, delay=100):
        '''Provide iterable source of data'''
        self.arduino.write(bytes([self.READ_DAQ_DELAY]) + (str(delay) + "x").encode())
        self.arduino.write(bytes([self.STREAM]))
        while True:
            raw = self.arduino.read_until()
            t, W = self.parse_raw(raw)
            yield W
        
def derivative(xvalue, yvalue):
    ydiff = np.array(yvalue[1:]) - np.array(yvalue[:-1])
    xdiff = np.array(xvalue[1:]) - np.array(xvalue[:-1])
    return ydiff/xdiff
            
if __name__ == '__main__':
    fig, ax = plt.subplots()
    scale = Scale(ax, 10, debug=True)
    port = scale.find_arduino()
    with serial.Serial(port, baudrate=115200) as arduino:
        scale.set_arduino(arduino)
        scale.tare()
        scale.handshake_arduino(print_handshake_message=True)
        ani = anim.FuncAnimation(fig, scale.update, scale.daq_stream, interval=100, blit=True, cache_frame_data=False)
        plt.show()

    true_max = max(scale.wdata)
    print(f'Max weight pulled was {true_max} kg.')
    slope = derivative(scale.tdata, scale.wdata)
    second_derivative = derivative(scale.tdata[:-1], slope)
    max_force_gen = max(slope)
    min_force_gen = min(slope)
    max_index = np.argmax(slope)
    min_index = np.argmin(slope)
    fig, ax = plt.subplots(2,1)
    ax[0].plot(scale.tdata, scale.wdata)
    ax[0].fill_between(scale.tdata[max_index:min_index], scale.wdata[max_index:min_index], alpha=0.5)
    ax[1].plot(scale.tdata[:-1], slope, label='1st Derivative')
    ax[1].plot(scale.tdata[1:-1], second_derivative, label='2nd Derivative')
    plt.show(block=True)
    current_date = datetime.datetime.fromtimestamp(time.time())
    day_month_year = f'{current_date.day}-{current_date.month}-{current_date.year}'
    hour_min_sec = f'{current_date.hour}:{current_date.min}:{current_date.second}'
    arm_used = input('Which arm? (left/right/both):')
    hold_size = input('Size of hold (in mm):')
    name_of_user = input('Name:')
    data_file = 'recorded_data.hdf5'
    print(f'Saving data to {data_file}')
    with hp.File('./' + data_file, 'r+') as hfile:
        grp = hfile.create_group(day_month_year + "/" + hour_min_sec)
        grp.attrs['arm_used'] = str(arm_used)
        grp.attrs['hold_size_mm'] = hold_size
        grp.attrs['name'] = str(name_of_user)
        grp['wdata'] = scale.wdata
        grp.attrs['sample_rate'] = 1/scale.dt
