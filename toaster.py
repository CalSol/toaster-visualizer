import datetime
import serial
import csv
import re

import numpy as np
import matplotlib.pyplot as plt

SERIAL_PATH = 'COM6'
SERIAL_BAUD = 115200

ELEMENT_COUNT = 8
WINDOW = 60 * 60  # in seconds

OUT_PREFIX = "toaster_"

TEXT_ALPHA = 0.75


# for testing only
TEST_LINE = "0: 73 2: 79 3: 80 4: 75 5: 81 6: 80 7: 82"

if __name__ == "__main__":
  start_time = datetime.datetime.now()
  out_filename = OUT_PREFIX + start_time.strftime("%Y%m%d_%H%M%S") + ".csv"

  # with serial.Serial(SERIAL_PATH, SERIAL_BAUD) as ser, open(out_filename, 'w', newline='') as csv_out:
  with open(out_filename, 'w', newline='') as csv_out:
    csvwriter = csv.writer(csv_out)
    csvwriter.writerow(['timestamp'] + list(range(0, ELEMENT_COUNT)))

    # initialize plot window and static elements
    fig, ax = plt.subplots(1, 1, constrained_layout=True)

    plots = list(map(lambda n: ax.plot([])[0], range(0, ELEMENT_COUNT)))
    print(plots)
    avg_line = ax.axhline(0)
    min_text = ax.text(0, 0, "", ha='right', va='top', alpha=TEXT_ALPHA)
    max_text = ax.text(0, 0, "", ha='right', va='bottom', alpha=TEXT_ALPHA)
    avg_text = ax.text(0, 0, "", ha='right', va='center', alpha=TEXT_ALPHA)
    ax.set_xlabel("time")
    ax.set_ylabel("temp")

    plt.ion()
    plt.draw()

    while True:
      line = ser.readline().decode('utf-8')
      # line = TEST_LINE
      line_time = datetime.datetime.now()
      delta_time = line_time.timestamp() - start_time.timestamp()
      print("[%s] received: %s" % (line_time.strftime("%H:%M:%S"), line))

      match = re.findall(r'(\d+):\s*(\d+\.?\d*)', line)
      match = list(map(lambda x: (int(x[0]), float(x[1])), match))

      if match:
        print("Decoded: %s" % (match))

        csvrow = list(map(lambda id: '', range(0, ELEMENT_COUNT)))
        for (id, val) in match:
          csvrow[id] = str(val)
        csvwriter.writerow([line_time.timestamp()] + csvrow)
        csv_out.flush()

        for (id, val) in match:
          if id >= ELEMENT_COUNT:
            print("(%s, %.1f) id out of range" % (id, val))
          else:
            plot = plots[id]
            plot.set_label("%s: %.1f" % (id,  val))
            xdata = plot.get_xdata()
            ydata = plot.get_ydata()
            while xdata.any() and xdata[0] < delta_time - WINDOW:
              xdata = xdata[1:]
              ydata = ydata[1:]
            xdata = np.append(xdata, delta_time)
            ydata = np.append(ydata, val)
            plot.set_xdata(xdata)
            plot.set_ydata(ydata)

        match_rev = list(map(lambda x: (x[1], x[0]), match))
        match_rev.sort()
        match_vals = list(map(lambda x: x[1], match))
        avg = sum(match_vals)/len(match_vals)
        min_text.set_x(delta_time)
        max_text.set_x(delta_time)
        avg_text.set_x(delta_time)
        min_text.set_y(match_rev[0][0])
        max_text.set_y(match_rev[-1][0])
        avg_text.set_y(avg)
        min_text.set_text("min %s: %.1f" % (match_rev[0][1], match_rev[0][0]))
        max_text.set_text("max %s: %.1f" % (match_rev[-1][1], match_rev[-1][0]))
        avg_text.set_text("avg(%s): %.1f, spd: %.1f" % (len(match_vals), avg, match_vals[-1] - match_vals[0]))

        ax.legend(loc=2)  # upper left
        ax.set_xlim(delta_time - WINDOW,  delta_time + 10)
        ax.set_ylim(0, 100)

        plt.draw()
        plt.pause(0.01)
