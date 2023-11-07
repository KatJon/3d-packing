
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

dir_th8 = 'results/rawdata/thpack8'
files = sorted(os.listdir(dir_th8))

get_boxes = lambda row: row[1]
get_usage = lambda row: row[3]

boxsum = 0
usagesum = 0
for f in files:
    name,_ = path.splitext(f)

    file = open(path.join(dir_th8, f))
    data = file.read()
    file.close()

    metrics = get_metrics(data)

    boxes = get_boxes(metrics)[-1]
    boxsum += boxes
    usage = get_usage(metrics)[-1]
    usagesum += usage

    print(f"{name} & {usage:.2f} & {boxes} \\\\")

print(f"{usagesum/len(files):.2f} & {boxsum} \\\\")
