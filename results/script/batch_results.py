
import os
from os import path
import re
import matplotlib.pyplot as plt

getstats = re.compile(r"%%%mzn-stat: solveTime=(\d+\.\d+)\n(\w+) (\w+) (\w+) (\w+) (\d+\.\d+)\n")

def get_metrics(data):
    matches = getstats.findall(data)

    # time, dataset, id, boxes, vol, usage = entry
    time = [float(e[0]) for e in matches]
    boxes = [int(e[3]) for e in matches]
    vol = [float(e[4]) / 10 ** 6 for e in matches]
    usage = [float(e[5]) for e in matches]

    return time, boxes, vol, usage

def draw_single_plot(X, Y, title, xlab, ylab, lin):
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    
    plt.scatter(X, Y,
        color='k',
        marker='.',
    )
    plt.plot(X, Y)
    plt.axhline(lin, color='tab:cyan')

dirs = [f"results/rawdata/thpack{i}" for i in range(1, 8)]

datasets = []

for d in dirs:
    files = sorted(os.listdir(d))

    setname = path.basename(d)

    datafiles = []

    for f in files:
        name,_ = path.splitext(f)

        file = open(path.join(d, f))
        data = file.read()
        file.close()

        met = get_metrics(data)

        datafiles.append((name, met))
        
    datasets.append((setname, datafiles))

def plot_dataset(data, title, getX, getY):
    plt.title(title)

    n = len(data)
    alpha = 2.0 / n

    for f,met in data:
        plt.scatter(getX(met), getY(met), 
            marker='.',
            s=9,
        )
    
    plt.xlabel("Czas [s]")

get_time = lambda row: row[0]
get_boxes = lambda row: row[1]
get_vol = lambda row: row[2]
get_usage = lambda row: row[3]

def get_int_summary(vals):
    minval = min(vals)
    maxval = max(vals)
    avgval = sum(vals) / len(vals)

    return f"{minval} & {avgval:.2f} & {maxval}"

def get_float_summary(vals):
    minval = min(vals)
    maxval = max(vals)
    avgval = sum(vals) / len(vals)

    return f"{minval:.2f} & {avgval:.2f} & {maxval:.2f}"

def get_values(data, get):
    return [get(row[1])[-1] for row in data]

def print_table_row(name, data):
    usage = get_float_summary(get_values(data, get_usage))
    boxes = get_int_summary(get_values(data, get_boxes))
    vol = get_float_summary(get_values(data, get_vol))
    
    print(f"{name} & {usage} & {boxes} & {vol} \\\\")

for nam,data in datasets:
    plot_dataset(data, f"{nam} wykorzystanie przestrzeni", 
        get_time,
        get_usage,
    )
    plt.ylabel("% wykorzystania przestrzeni",)
    plt.savefig(f"results/graphs/batch/{nam}_usage.png", dpi=250)
    plt.close()

    plot_dataset(data, f"{nam} pozostawione przedmioty", 
        get_time,
        get_boxes,
    )
    plt.ylabel("sztuki",)
    plt.savefig(f"results/graphs/batch/{nam}_boxes.png", dpi=250)
    plt.close()

    plot_dataset(data, f"{nam} pozostawiony ładunek", 
        get_time,
        get_vol,
    )
    plt.ylabel("[$m^3$]",)
    plt.savefig(f"results/graphs/batch/{nam}_vol.png", dpi=250)
    plt.close()

    print_table_row(nam, data)
