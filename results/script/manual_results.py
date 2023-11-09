
import re
import matplotlib.pyplot as plt

src = "results/rawdata/manual/manual_4h_thpack_001.log"

file = open(src)
data = file.read()
file.close()

getstats = re.compile(r"%%%mzn-stat: solveTime=(\d+\.\d+)\n(\w+) (\w+) (\w+) (\w+) (\d+\.\d+)\n")

matches = getstats.findall(data)

# time, dataset, id, boxes, vol, usage = entry
time = [float(e[0]) for e in matches]
boxes = [int(e[3]) for e in matches]
vol = [float(e[4]) / 10 ** 6 for e in matches]
usage = [float(e[5]) for e in matches]

def draw_plot(X, Y, title, xlab, ylab, lin):
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    
    plt.scatter(X, Y,
        color='k',
        marker='.',
    )
    plt.plot(X, Y)
    plt.axhline(lin, color='tab:cyan')

maxus = max(usage)
draw_plot(time, usage,
    f"Volume utilization max={maxus:.2f}%",
    "Time [s]",
    "%",
    maxus,
)
plt.savefig("results/graphs/manual/usage.png")
plt.close()

minbox = min(boxes)
draw_plot(time, boxes,
    f"Remaining items min={minbox}",
    "Time [s]",
    "items",
    minbox
)
plt.savefig("results/graphs/manual/boxes.png")
plt.close()

minvol = min(vol)
draw_plot(time, vol,
    f"Remaining volume min={minvol:.2f} m$^3$",
    "Time [s]",
    "[m$^3$]",
    minvol
)
plt.savefig("results/graphs/manual/volume.png")
plt.close()
