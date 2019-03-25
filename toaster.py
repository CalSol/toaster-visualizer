import datetime
import serial

import numpy as np
import matplotlib.pyplot as plt

SERIAL_PATH = 'COM6'
SERIAL_BAUD = 115200

ELEMENT_COUNT = 8
SAMPLES = 60 * 60

OUT_PREFIX = "toaster_"

TEST_LINE = "0: 73 2: 79 3: 80 4: 75 5: 81 6: 80 7: 82"

if __name__ == "__main__":
  start_time = datetime.datetime.now()
  out_filename = OUT_PREFIX + start_time.strftime("%Y%m%d_%H%M%S") + ".csv"

  with serial.Serial(SERIAL_PATH, SERIAL_BAUD) as ser, open(out_filename, "w") as csv_out:
    # initialize plot window and static elements
    fig, ax = plt.subplots(2, 1, constrained_layout=True)

    plots = map(lambda n: ax[0].plot([]),range(0, ELEMENT_COUNT))
    avg_line = ax[0].axhline(0)
    min_text = ax[0].text(0, 0, "")
    max_text = ax[0].text(0, 0, "")
    avg_text = ax[0].text(0, 0, "")
    ax[0].set_xlabel("time")
    ax[0].set_ylabel("temp")

    plt.ion()
    plt.draw()

    while True:
      line = ser.readline()
      line_time = datetime.datetime.now()
      print("[%s] received: %s" % (line_time.strftime("%H:%M:%S"), line))

