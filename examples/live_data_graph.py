
import sys
import os

import argparse
import socket
from collections import deque
from functools import partial

import grpc
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation, ticker

def add_minknower_api_locally():
    # Makes sure the local version of Minknower API is used,
    # so you can edit the code locally and run it without rebuilding.
    minknower_local_path = os.path.abspath(f"{os.path.abspath(os.path.dirname(__file__))}/..")
    sys.path.insert(0, minknower_local_path)
    print("adding path ", minknower_local_path)

add_minknower_api_locally()

from minknower.device import Device
from minknower.flowcell import Flowcell
from minknower.manager import MinKnow
from minknower.acquisition import Acquisition, MinknowStatus


# Draw a live animated plot: https://stackoverflow.com/questions/49405499/real-time-matplotlib-plotting


def main(machine_ip_address):
    print(f"Connecting to machine at: {machine_ip_address!s}")

    # Creates the MinKnow manager, which connects to your machine's MinKnow instance.
    mk = MinKnow(server=machine_ip_address)

    # Gets the first flowcell detected.
    flowcell: Flowcell = next(mk.flow_cells())
    device: Device = Device(flowcell.channel)

    # Acquisition configuration.
    acquirer = Acquisition(flowcell.channel)

    sampling_rate = device.sample_rate

    # Starts an acquisiton session if one wasn't already in progress.
    if acquirer.current_status == MinknowStatus.READY:
        print("Acquistion is not in progress). Starting one now.")
        acquirer.start()
        print("Acquistion started!")

    # Get the device calibration (for converting the signal to picoamperes)
    calibration = device.get_calibration()
    def scale_raw_current(raw, calibration):
        # Borrowed from raw_signal_utils
        digitisation = calibration.digitisation
        offsets = np.array(calibration.offsets)
        ranges = np.array(calibration.pa_ranges)
        return (raw + offsets) / (digitisation / ranges)

    print(f"calibration: {calibration!s}")

    # First channel to look at
    first_channel = 19
    # Last channel to look at
    last_channel = 19
    # How many samples to get per chunk
    samples = np.int(sampling_rate/10)

    # Makes a function we can call multiple times
    # That fetches a new data chunk with each call.
    get_chunk = partial(flowcell.get_signal_bytes_by_samples, samples, first_channel=first_channel, last_channel=last_channel)

    def init():
        line.set_ydata([np.nan] * len(x))
        return (line,)

    def get_data_from_channel(channel):
        """Extracts data from a channel, converting it to numpy floats.
        """
        data = np.frombuffer(channel.data, dtype=np.int16)
        return data

    def animate(i):
        chunks_by_channel = next(get_chunk()).channels

        raw_signals = np.array(list(map(get_data_from_channel, chunks_by_channel)))
        # Converts to picoamperes.
        signals = scale_raw_current(raw_signals, calibration)

        # Only plot the first channel (for simplicity)
        signal = signals[0]
        data.extend(signal)
        line.set_ydata(data)
        #print(f"min: {np.min(signal)}, max: {np.max(signal)}")
        return (line,)


    # Graphing setup
    len_x = samples * 2
    x = np.arange(0, len_x).tolist()
    data = deque(np.zeros(len_x), maxlen=len_x)

    fig, ax = plt.subplots()
    (line,) = ax.plot(x, data, lw=2)
    ax.set_ylim(-70, 20)

    ax.set_title(f"Channel {first_channel} Current")
    ax.set_ylabel("picoAmps (pA)")
    ax.set_xlabel("Time")

    #ax.get_xaxis().set_minor_locator(ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(b=True, which="major", color="grey", linewidth=1.0)
    ax.grid(b=True, which="minor", color="lightgrey", linewidth=0.5)
    fig.tight_layout()
    
    ani = animation.FuncAnimation(
        fig, animate, init_func=init, interval=100, blit=True, save_count=10
    )

    plt.show()



def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_args():
    import argparse

    parser = argparse.ArgumentParser(description="A simple example of live data acquistion")
    parser.add_argument(
        "-i",
        "--ip",
        action="store",
        default=get_ip_address(),
        help="IP addresss of the machine running MinKnow. I really need to do some additional security checks.",
    )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    ip_address = args.ip
    main(ip_address)
