import sys
import inspect
import os
import math
from os import path

import logging
logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    # level=logging.DEBUG,
    level=logging.ERROR,
    datefmt='%m/%d/%Y %H:%M:%S'
)

INDENT = '  '

class Instance:
    def __init__(self, i, seed, L, W, H, dataset):
        self.i = i
        self.seed = seed
        self.L = L
        self.W = W
        self.H = H
        self.dataset = dataset
        self.types = []
    
    def addType(self, sizes, vert, count):
        self.types.append(
            (sizes, vert, count)
        )

    def addType(self, typ):
        self.types.append(typ)

    def getTypeCount(self):
        return len(self.types)

    def getSizeArray(self):
        sizes = ''.join(map(
            lambda t: INDENT + f'{t[0][0]},{t[0][1]},{t[0][2]} |\n', 
            self.types
        ))
        return f'size = [|\n{sizes}|];\n'

    def getVerticalityArray(self):
        verticality = ''.join(map(
            lambda t: INDENT + f'{t[1][0]},{t[1][1]},{t[1][2]} |\n', 
            self.types
        ))
        return f'verticality = [|\n{verticality}|];\n'

    def getBoxCountArray(self):
        box_count = ''.join(map(
            lambda t: INDENT + f'{t[2]},\n', 
            self.types
        ))
        return f'box_count = [\n{box_count}];\n'


    def asMiniZincModel(self):
        header = inspect.cleandoc(f'''
            DATASET = \"{self.dataset}\";
            INSTANCE = \"{f'{self.i:03}'}\";

            WIDTH = {self.W};
            HEIGHT = {self.H};
            LENGTH = {self.L};

            NO_OF_SHAPES = {len(self.types)};

        ''')

        return '\n'.join([
            header,
            self.getSizeArray(),
            self.getVerticalityArray(),
            self.getBoxCountArray(),
        ])

def getLineOfInts(file):
    line = file.readline()
    chunks = line.split()

    return map(int, chunks)

def parseInstance(file, dataset):
    instdesc = tuple(getLineOfInts(file))
    i = instdesc[0]
    seed = instdesc[1] if len(instdesc) > 1 else None
    L,W,H = getLineOfInts(file)
    inst = Instance(i, seed, L, W, H, dataset)

    k, = getLineOfInts(file)
    logging.info('Instance %4d: (%d, %d, %d) %d', i, L, W, H, k)
    
    for j in range(k):
        j1, l, vl, w, vw, h, vh, c = getLineOfInts(file)

        if (j + 1 != j1):
            logging.error('Mismatch of box type definition %d for type %d', i, j)

        typ = ((l,w,h), (vl,vw,vh), c)
        inst.addType(typ)
    
    if (inst.getTypeCount() != k):
        logging.error('Mismatch of box types in instance %d', i)

    return inst

def printStats(instances):
    box_count = [sum(t[2] for t in i.types) for i in instances]
    minsum = min(box_count)
    maxsum = max(box_count)

    print(f"Min: {minsum} Max: {maxsum}")

def process(infile, outdir):
    dataset,_ = path.splitext(path.basename(infile))

    try:
        with open(infile) as file:
            N, = getLineOfInts(file)
            logging.info("Number of instances in file: %d", N)

            instances = [None for i in range(N)]

            for i in range(N):
                inst = parseInstance(file, dataset)
                instances[i] = inst

            printStats(instances)
    except IOError:
        logging.error("Cannot open file %s!", infile)
        return

    logging.info("Finished parsing input file.")

    output_path = path.join(outdir, dataset)
    if not path.exists(output_path):
        try:
            os.mkdir(output_path)
        except OSError:
            logging.error('Cannot create output directory: %s', output_path)
        else:
            logging.info('Created output directory: %s', output_path)
    elif not path.isdir(output_path):
        logging.error('Path conflict: output directory')

    for inst in instances:
        inst_name = f"{inst.dataset}_{f'{inst.i:03}'}.dzn"
        inst_path = path.join(output_path, inst_name)

        if path.exists(inst_path):
            logging.warning("Overwriting existing instance: %s", inst_path)
        
        with open(inst_path, "w") as f:
            f.write(inst.asMiniZincModel())

            logging.info("Instance saved successfully: %s", inst_path)

    logging.info("Finished processing.")
    return

def main():
    if len(sys.argv) < 3:
        print("Not enough arguments!")
        print("usage: python3 convert.py <input_set> <output_directory>")
        
        return

    logging.info("Conversion of test cases started")

    infile = sys.argv[1]
    outdir = sys.argv[2]

    if not path.exists(infile):
        logging.error("Input file doesn't exist!")

        return
    elif not path.isfile(infile):
        logging.error("Not a file: %s", infile)

        return

    logging.info("Source: %s", infile)

    if not path.exists(outdir):
        logging.error("Output directory doesn't exist!")

        return
    elif not path.isdir(outdir):
        logging.error("Not a directory: %s", outdir)

        return
    
    logging.info("Output directory: %s", outdir)

    process(infile, outdir)

if __name__ == "__main__":
    main()
