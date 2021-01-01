#!/usr/bin/env python

#from __future__ import print_function
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
from scipy.ndimage import binary_dilation
import imageio
from matplotlib.ticker import FuncFormatter

def double_ticks(x, pos):
    return int(x/2)

inputFilename = sys.argv[1]

input_image = imageio.imread(inputFilename)
if(len(input_image.shape)) > 2:
    input_image=input_image[:,:,:-1]              #These 3 lines are in case the image is a 4 channel png
    input_image = np.asarray(input_image)
    input_image = np.dot(input_image, [0.299, 0.587, 0.114])
input_image= (input_image - np.min(input_image))/(np.max(input_image)-np.min(input_image))
un_input = imageio.imread(inputFilename[:-4]+"_un.jpg")
for i in range(1,6):
    maskFilename = inputFilename[:-4]+"_mask_"+str(i)+".png"
    Mask = imageio.imread(maskFilename)/255
    Borderu = binary_dilation(Mask)-Mask
    Borderu = (255*Borderu).astype(np.uint8)

    rgb_img = np.stack((input_image,)*3, axis=-1)
    rgb_img = (255*rgb_img).astype(np.uint8)

    rgb_img[:,:,0][np.where(Borderu > 0)] = 255
    rgb_img[:,:,1][np.where(Borderu > 0)] = 0
    rgb_img[:,:,2][np.where(Borderu > 0)] = 0

    border_image = rgb_img
    mask_image = Mask

    tick_rate = 10
    if mask_image.shape[0] > 78:
        tick_rate = 20
    if mask_image.shape[0] < 32:
        tick_rate = 4
    print(input_image.shape)
    print(mask_image.shape)
    fig,ax = plt.subplots(1,3)
    ax[0].imshow(un_input,cmap="gray")
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
    plt.savefig(inputFilename[:-4]+'_rating='+str(i)+'.png', bbox_inches='tight')
    #plt.show()
