import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mplt
import pandas as pd

import serial
import serial.tools.list_ports

def find_arduino(port=None):
    """Get the name of the port that is connected to Arduino."""
    if port is None:
        ports = serial.tools.list_ports.comports()
        print(ports)
        for p in ports:
            if p.manufacturer is not None and "Arduino" in p.manufacturer:
                port = p.device
    return port


def handshake_arduino(
    arduino, sleep_time=1, print_handshake_message=False, handshake_code=0
):
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
    arduino.write(bytes([handshake_code]))

    # Read in what Arduino sent
    handshake_message = arduino.read_until()

    # Send and receive request again
    arduino.write(bytes([handshake_code]))
    handshake_message = arduino.read_until()

    # Print the handshake message, if desired
    if print_handshake_message:
        print("Handshake message: " + handshake_message.decode())

    # Reset the timeout
    arduino.timeout = timeout


def parse_raw(raw):
    """Parse bytes output from Arduino."""
    raw = raw.decode()
    if raw[-1] != "\n":
        raise ValueError(
            "Input must end with newline, otherwise message is incomplete."
        )

    t, V = raw.rstrip().split(",")

    return int(t), int(V) 

def daq_stream(arduino, n_data=100, delay=20):
    """Obtain `n_data` data points from an Arduino stream
    with a delay of `delay` milliseconds between each."""
    # Specify delay
    arduino.write(bytes([READ_DAQ_DELAY]) + (str(delay) + "x").encode())

    # Initialize output
    time_ms = np.empty(n_data)
    voltage = np.empty(n_data)

    # Turn on the stream
    arduino.write(bytes([STREAM]))

    # Receive data
    i = 0
    while i < n_data:
        raw = arduino.read_until()

        try:
            t, V = parse_raw(raw)
            time_ms[i] = t
            voltage[i] = V
            i += 1
        except:
            pass

    # Turn off the stream
    arduino.write(bytes([ON_REQUEST]))

    return pd.DataFrame({'time (ms)': time_ms, 'voltage (V)': voltage})


if __name__ == '__main__':
    HANDSHAKE = 0
    VOLTAGE_REQUEST = 1
    ON_REQUEST = 2
    STREAM = 3
    READ_DAQ_DELAY = 4

    port = find_arduino()
    with serial.Serial(port, baudrate=115200) as arduino:
        handshake_arduino(arduino, handshake_code=HANDSHAKE, print_handshake_message=True)
        df = daq_stream(arduino, n_data=100, delay=20)

    time = df['time (ms)'].to_numpy().astype(float)/1000
    volts = df['voltage (V)'].to_numpy().astype(float)
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.plot(time, volts)
    plt.show()

    
        

        
    
