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
    current_date = datetime.datetime.fromtimestamp(time.time())
    day_month_year = f'{current_date.day}-{current_date.month}-{current_date.year}'
    hour_min_sec = f'{current_data.hour}:{current_date.min}:{current_date.second}'
    arm_used = input('Which arm? (left/right/both):')
    hold_size = input('Size of hold (in mm):')
    name_of_user = input('Name:')
    data_file = 'recorded_data.hdf5'
    print(f'Saving data to {data_file}')
    with hp.File('./' + data_file, 'r+') as hfile:
        grp = hfile.create_group(day_month_year + "/" + hour_min_sec)
        grp['arm_used'] = arm_used
        grp['hold_size_mm'] = hold_size
        grp['name'] = name_of_user
        grp['wdata'] = scale.wdata
        grp['sample_rate'] = 1/scale.dt
        
# Maybe I can make the moving/updating frame work later. For now the x-axis is static while the line gets plotted        
"""            
    def update(self, w):
        ''' Update the data by shifting the oldest data out and pushing the newest weight into the last slot.'''
        if self.debug:
            print(f'w is {w}')
        self.tdata = shift(self.tdata, -1, cval=self.tdata[-1] + 0.1)
        self.wdata = shift(self.wdata, -1, cval=w)
        if w > self.maxw:
            self.maxw = w + 5
            self.ax.set_ylim(0, self.maxw)
        self.xlow += self.dt
        self.xhigh += self.dt
        self.ax.set_xlim(self.xlow, self.xhigh)
        self.line.set_data(self.tdata, self.wdata)
        return self.line,
"""
    
