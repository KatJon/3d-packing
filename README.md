Constraint programming methods in three-dimensional container packing
===

Supplementary materials
---

This repository contains supplementary materials to the "Constraint programming methods in three-dimensional container packing" report.

### Requirements

* Python 3
* MiniZinc
* OR-Tools

### Running the model

```
minizinc --solver ortools -s -p $CPUS -a -f $MODEL $DATA
```
where
* `$CPUS` is the number of cores,
* `$MODEL` is the path to the model (if running from repository root: `model/model.mzn`),
* `$DATA` is the path to the input data in a proper format (e.g. `data\converted\thpack1\thpack1_001.dzn`).

### Running visualization

The visualization app can be run using any http server, for example, in local environment a python module can be used:

```
python -m http.server 8080 -d model/visualization
```