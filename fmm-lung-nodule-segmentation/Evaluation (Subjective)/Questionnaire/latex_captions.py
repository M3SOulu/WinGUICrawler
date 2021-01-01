#!/usr/bin/env python

#from __future__ import print_function
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
import imageio

INPUT_FOLDER = sys.argv[1]
nodules = []
#walks the input directory and finds input images and their paths
for root, dirs, files in os.walk(INPUT_FOLDER):
    path = root.split(os.sep)
    for file in files:
        if file[-1] == "g" and file[-2]=="n" and file[-3]=="p":
            stringa = ""
            for p in path:
                stringa+=p+"/"
            nodules.append((file,stringa))

#reads and normalizes input image
for nod in nodules:
    inputFilename = nod[1]+nod[0]
    print(inputFilename)
    image = imageio.imread(inputFilename)
    fig,ax = plt.subplots(1,1)
    ax.imshow(image)
    plt.axis("off")
    ax.set_title("ZIO CAN")
    plt.show()
