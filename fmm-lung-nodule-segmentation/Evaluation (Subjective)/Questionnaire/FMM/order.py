#!/usr/bin/env python

#from __future__ import print_function
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
import imageio
import scipy.ndimage as ndi

def double_ticks(x, pos):
    return int(x/2)

INPUT_FOLDER = sys.argv[1]
nodules = []
#walks the input directory and finds input images and their paths
for root, dirs, files in os.walk(INPUT_FOLDER):
    path = root.split(os.sep)
    for file in files:
        if file[-1] == "g" and file[-2]=="p" and file[-3]=="j":
            stringa = ""
            for p in path:
                stringa+=p+"/"
            nodules.append((file,stringa))

#reads and normalizes input image
for nod in nodules:
    print("------------------------------------------")
    print(nod)
    print("------------------------------------------")

    inputFilename = nod[1]+nod[0]
    borderFilename = inputFilename[:-7]+".png_border.png"
    maskFilename = inputFilename[:-7]+".png_segmented.png"

    input_image = imageio.imread(inputFilename)
    border_image = imageio.imread(borderFilename)
    mask_image = imageio.imread(maskFilename)

    tick_rate = 10
    if mask_image.shape[0] > 78:
        tick_rate = 20
    if mask_image.shape[0] < 32:
        tick_rate = 4
    print(input_image.shape)
    print(mask_image.shape)
    fig,ax = plt.subplots(1,3)
    ax[0].imshow(input_image,cmap="gray")
    ax[0].set_title("Input")
    ax[1].imshow(border_image)
    ax[1].set_title("Boundary")
    ax[2].set_title("Mask")
    ax[2].set_xlabel("mm")
    ax[2].set_ylabel("mm")
    ax[1].set_xlabel("mm")
    ax[1].set_ylabel("mm")
    ax[2].imshow(mask_image,cmap="gray")
    ax[0].axis('off')
    for axi in ax.flat:
        axi.xaxis.set_major_locator(plt.MultipleLocator(tick_rate))
        axi.yaxis.set_major_locator(plt.MultipleLocator(tick_rate))
        axi.yaxis.set_minor_locator(plt.MultipleLocator(2))
        axi.xaxis.set_minor_locator(plt.MultipleLocator(2))
        axi.xaxis.set_major_formatter(FuncFormatter(double_ticks))
        axi.yaxis.set_major_formatter(FuncFormatter(double_ticks))
    fig.tight_layout(pad=1.2)


    """start, end = ax[1].get_xlim()
    x_axis = np.arange(start+0.5,end+0.5,10).astype(int)
    x_ticks = np.arange(start+0.5,end+0.5,5).astype(int)
    ax[1].set_xticks(x_axis)
    ax[1].set_xticklabels(x_ticks)
    ax[1].set_yticks(x_axis)
    ax[1].set_yticklabels(x_ticks)
    ax[2].set_xticks(x_axis)
    ax[2].set_xticklabels(x_ticks)
    ax[2].set_yticks(x_axis)
    ax[2].set_yticklabels(x_ticks)    """
    #plt.xticks(x_axis, x_ticks)
    #ax[1].axis('off')
    #ax[2].axis('off')
    plt.savefig(inputFilename[:-7]+'_ordered_fmm.png', bbox_inches='tight')
    #plt.show()
