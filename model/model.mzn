% Author: Szymon Wróbel 236761

include "globals.mzn";

% ========================
% === INPUT PARAMETERS ===
% ========================

par opt bool: SIMPLE;

par string: DATASET;
par string: INSTANCE;

set of int: DIMS = 1..3;

par int: WIDTH;
par int: LENGTH;
par int: HEIGHT;

array[DIMS] of int: MIN_DIM = [0, 0, 0];
array[DIMS] of int: MAX_DIM = [WIDTH, LENGTH, HEIGHT];

par int: NO_OF_SHAPES;
set of int: SHAPES = 1..NO_OF_SHAPES;
array[SHAPES] of SHAPES: SHAPES_LIST = [i | i in SHAPES];

int: MAX_SIZE = max(MAX_DIM);

array[SHAPES, DIMS] of int: size;
array[SHAPES, DIMS] of int: verticality;
array[SHAPES] of int: box_count;

int: N = sum(box_count);
set of int: BOXES = 1..N;

int: NO_OF_ROTATIONS = 6;
set of int: ROTATIONS = 1..NO_OF_ROTATIONS;

array[ROTATIONS, DIMS] of DIMS: ROTATION = [|
    1, 2, 3 |
    1, 3, 2 |
    2, 1, 3 |
    2, 3, 1 |
    3, 1, 2 |
    3, 2, 1 |
|];

% =================
% === VARIABLES ===
% =================

array[BOXES] of var SHAPES: shape;
array[BOXES, DIMS] of var 0..MAX_SIZE: pos;
array[BOXES] of var bool: packed;
array[BOXES] of var ROTATIONS: rotation;

function var DIMS: get_dim(BOXES: i, DIMS: d) = ROTATION[rotation[i], d];
function DIMS: fget_dim(BOXES: i, DIMS: d) = ROTATION[fix(rotation[i]), d];

% ===================
% === CONSTRAINTS ===
% ===================

% Ensure number of boxes of each type is valid
constraint global_cardinality(shape, SHAPES_LIST, box_count);

% Basic constraint on box origin position
constraint forall (i in BOXES, d in DIMS)(
    MIN_DIM[d] <= pos[i, get_dim(i, d)] 
    /\ 
    pos[i, get_dim(i, d)] + size[shape[i], get_dim(i, d)] <= MAX_DIM[d]
);

% Ensure that boxes can be placed horizontally only in allowed axes
constraint forall (i in BOXES) (
     verticality[shape[i], get_dim(i, 3)] == 1
);

% Ensure boxes don't overlap
constraint diffn_nonstrict_k(
    array2d(BOXES, DIMS, [
        pos[i, get_dim(i, d)]
    | i in BOXES, d in DIMS
    ]),
    array2d(BOXES, DIMS, [
        bool2int(packed[i]) * size[shape[i], get_dim(i, d)]
    | i in BOXES, d in DIMS
    ]),
);


% =========================
% === SYMMETRY BREAKING ===
% =========================

% Break symmetry between box shapes
constraint increasing(i in BOXES)(shape[i]);

% =============
% === SOLVE ===
% =============

function var int: volume_of_shape(var SHAPES: s) = 
    size[s, 1] * size[s, 2] * size[s, 3];
function     int: fvolume_of_shape(SHAPES: s) = 
    size[s, 1] * size[s, 2] * size[s, 3];

function var int: volume_of_box(BOXES: i) = volume_of_shape(shape[i]);
function     int: fvolume_of_box(BOXES: i) = fvolume_of_shape(fix(shape[i]));

function var int:  not_packed = sum(i in BOXES) (bool2int(not packed[i]));
function     int: fnot_packed = sum(i in BOXES) (bool2int(not fix(packed[i])));

function var int:  left_volume = sum(i in BOXES)
  (bool2int(not packed[i]) * volume_of_box(i));
function     int: fleft_volume = sum(i in BOXES)
  (bool2int(fix(not packed[i])) * fvolume_of_box(i));

solve minimize left_volume();

% ==============
% === OUTPUT ===
% ==============

function int: used_volume = sum(i in BOXES where fix(packed[i]))
  (product(d in DIMS)(size[fix(shape[i]), d]));

function float: volume_utilization = 100 * used_volume() / product(d in DIMS)(MAX_DIM[d]);

function string: print_header = join("\n", [
    join(" ", [
      DATASET,
      INSTANCE,
      show(fnot_packed()),
      show(fleft_volume()),
      format(3, 2, volume_utilization()),
    ]),	
    join(" ", [
      show(WIDTH),
      show(LENGTH),
      show(HEIGHT),
    ]),
]) ++ "\n";

function string: print_box(BOXES: i) = if not fix(packed[i]) then "" else
    concat([
        concat(d in DIMS)(show(pos[i, fget_dim(i, d)]) ++ " "),
        concat(d in DIMS)(show(size[shape[i], fget_dim(i, d)]) ++ " "),
        show(shape[i]),
        "\n",
    ])
endif;

function array[int] of string: output_debug() = [
    print_header(),
    concat([print_box(i) | i in BOXES]),
];

function array[int] of string: output_perf() = [
    join(" ", [
      DATASET,
      INSTANCE,
      show(fnot_packed()),
      show(fleft_volume()),
      format(3, 2, volume_utilization()),
    ]),
];

function array[int] of string: get_output() = 
    if occurs(SIMPLE) then 
        output_perf()
    else
        output_debug()
    endif;

output get_output();
