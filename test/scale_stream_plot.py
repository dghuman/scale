import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mplt
import matplotlib.animation as anim
from scipy.ndimage import shift

import serial
import serial.tools.list_ports

class scale:
    def __init__(self, ax, maxt, dt=0.1):
        self.port = None
        self.dt = dt
        self.ax = ax
        self.maxt = maxt
        self.maxw = 10
        self.tdata = np.zeros((int(maxt/dt)))
        self.wdata = np.zeros((int(maxt/dt)))
        self.line = mplt.lines.Line2D(self.tdata, self.wdata)
        self.ax.add_line(self.line)
        self.ax.set_xlim(0, self.maxt)
        self.ax.set_ylim(0, self.maxw)
        
        self.HANDSHAKE = 0
        self.VOLTAGE_REQUEST = 1
        self.ON_REQUEST = 2
        self.STREAM = 3
        self.READ_DAQ_DELAY = 4
        self.TARE = 5

    def set_lims(self, xlims, ylims):
        self.ax.set_xlim(xlims[0], xlims[1])
        self.ax.set_ylim(ylims[0], ylims[1])
            
    def update(self, w):
        if w > self.maxw:
            self.maxw = w + 5
            self.ax.set_ylim(0, self.maxw)
        
            
        
    def find_arduino(self):
        """Get the name of the port that is connected to Arduino."""
        if self.port is None:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if p.manufacturer is not None and "Arduino" in p.manufacturer:
                    port = p.device
        self.port = port
        return port

    def handshake_arduino(self, arduino, sleep_time=1, print_handshake_message=False):
        """Make sure connection is established by sending
        and receiving bytes."""
        # Close and reopen
        arduino.close()
        arduino.open()

        # Chill out while everything gets set
        time.sleep(sleep_time)

        # Set a long timeout to complete handshake
        timeout = arduino.timeout
        arduino.timeout = 2

        # Read and discard everything that may be in the input buffer
        _ = arduino.read_all()

        # Send request to Arduino
        arduino.write(bytes([self.HANDSHAKE]))

        # Read in what Arduino sent
        handshake_message = arduino.read_until()

        # Send and receive request again
        arduino.write(bytes([self.HANDSHAKE]))
        handshake_message = arduino.read_until()

        # Print the handshake message, if desired
        if print_handshake_message:
            print("Handshake message: " + handshake_message.decode())

        # Reset the timeout
        arduino.timeout = timeout
        return 1

    def parse_raw(self, raw):
        """Parse bytes output from Arduino."""
        raw = raw.decode()
        if raw[-1] != "\n":
            raise ValueError(
                "Input must end with newline, otherwise message is incomplete."
            )

        t, W = raw.rstrip().split(",")
        return int(t), float(W) 

    def daq_stream(self, arduino, n_data=100, delay=100):
        """Obtain `n_data` data points from an Arduino stream
        with a delay of `delay` milliseconds between each."""
        # Specify delay
        arduino.write(bytes([READ_DAQ_DELAY]) + (str(delay) + "x").encode())

        # Initialize output
        time_ms = np.empty(n_data)
        weight = np.empty(n_data)

        # Turn on the stream
        arduino.write(bytes([STREAM]))

        # Receive data
        i = 0
        while i < n_data:
            raw = arduino.read_until()
            try:
                t, W = parse_raw(raw)
                time_ms[i] = t
                weight[i] = W
                i += 1
            except:
                pass

        # Turn off the stream
        arduino.write(bytes([ON_REQUEST]))

        return time_ms, weight 


if __name__ == '__main__':
    HANDSHAKE = 0
    VOLTAGE_REQUEST = 1
    ON_REQUEST = 2
    STREAM = 3
    READ_DAQ_DELAY = 4
    TARE = 5

    port = find_arduino()
    with serial.Serial(port, baudrate=115200) as arduino:
        handshake_arduino(arduino, handshake_code=HANDSHAKE, print_handshake_message=True)
        time_ms, weight = daq_stream(arduino, n_data=100, delay=100)

    time = time_ms/1000
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.plot(time, weight)
    plt.show()

    
        

        
    
