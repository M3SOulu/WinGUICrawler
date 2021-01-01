#!/usr/bin/env python
#from __future__ import print_function
import sys
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator,PercentFormatter)

def signif(x, digits=3):
    if x == 0 or not math.isfinite(x):
        return x
    digits -= math.ceil(math.log10(abs(x)))
    return round(x, digits)

stringhette = ["Round","Semi-transparent","Cavitary","Irregular"]
for stringhetta in stringhette:
    INPUT_FOLDER = stringhetta#sys.argv[1]

    """for i in range(0,18):
        print("iou_fmm["+str(i)+"],",end="")
    exit()"""
    labels = []
    iou_fmm = []
    iou_ac = []
    scores_list = []
    longerr_fmm = []
    longerr_ac = []
    shorterr_fmm = []
    shorterr_ac = []

    scores = open(INPUT_FOLDER+"/scores.txt")
    for f in scores:
        scores_list.append(f[:-1].split("&"))
    scores_list.sort()
    for s in scores_list:
        iou_fmm.append(float(s[1]))
        iou_ac.append(float(s[4]))
        longerr_fmm.append(float(s[2]))
        longerr_ac.append(float(s[5]))
        shorterr_fmm.append(float(s[3]))
        shorterr_ac.append(float(s[6]))

    if INPUT_FOLDER[-1] == "/":
        INPUT_FOLDER = INPUT_FOLDER[:-1]
    if True:

        n = len(scores_list)
        plt_scale = int(n/18)
        print(plt_scale)
        x = np.arange(1,n+1,1)
        fig,ax = plt.subplots(1,1)
        ax.plot(x, iou_fmm, 'ro--', linewidth=1, markersize=3)
        ax.plot(x, iou_ac, 'bo--', linewidth=1, markersize=3)
        ax.set_xlim((1, n))
        ax.set_ylim((0, 1))
        ax.set_xticks(x)
        ax.set_ylabel("IoU",fontsize=16)
        ax.set_xlabel("Index",fontsize=16)
        red_patch = mpatches.Patch(color='red', label='FMM - IoU')
        blue_patch = mpatches.Patch(color='blue', label='AC - IoU')
        ax.legend(handles=[blue_patch,red_patch])
        ax.yaxis.set_major_locator(MultipleLocator(0.1))
        ax.yaxis.set_minor_locator(MultipleLocator(0.05))
        ax.grid(which='both')
        fig.set_size_inches((5.5*plt_scale, 4.2), forward=False)
        #plt.show()
        plt.savefig("Graphs/paper/"+INPUT_FOLDER+"_iou_graph.png",bbox_inches='tight',pad_inches=0.01)

        print("\\begin{figure}[h!]")
        print("\\centering")
        print("\\includegraphics[width=0.9\linewidth]{img/"+INPUT_FOLDER+"_iou_graph.png}")
        print("\\caption{"+INPUT_FOLDER+" - Intersection over Union}")
        print("\\label{fig:"+INPUT_FOLDER+"_iou_graph}")
        print("\\end{figure}")
        print("")
        fig,ax = plt.subplots(1,1)
        ax.plot(x, longerr_fmm, color='maroon',marker='o',linestyle='dashed', linewidth=1, markersize=3)
        ax.plot(x, longerr_ac, color='midnightblue',marker='o',linestyle='dashed', linewidth=1, markersize=3)
        ax.plot(x, shorterr_fmm, color='salmon',marker='o',linestyle='dashed', linewidth=1, markersize=3)
        ax.plot(x, shorterr_ac, color='royalblue',marker='o',linestyle='dashed', linewidth=1, markersize=3)
        ax.set_xlim((1, n))
        ax.set_ylim(bottom=0)
        ax.set_ylim(top=245)
        ax.set_xticks(x)
        ax.yaxis.set_major_formatter(PercentFormatter())
        ax.set_ylabel("Diameter relative error",fontsize=16)
        ax.set_xlabel("Index",fontsize=16)
        maroon_patch = mpatches.Patch(color='maroon', label='FMM - Long-axis')
        midnightblue_patch = mpatches.Patch(color='midnightblue', label='AC - Long-axis')
        salmon_patch = mpatches.Patch(color='salmon', label='FMM - Short-axis')
        royalblue_patch = mpatches.Patch(color='royalblue', label='AC - Short-axis')
        ax.legend(handles=[maroon_patch,midnightblue_patch,salmon_patch,royalblue_patch])
        ax.yaxis.set_major_locator(MultipleLocator(20))
        ax.yaxis.set_minor_locator(MultipleLocator(10))
        ax.grid(which='both')
        fig.set_size_inches((5.5*plt_scale, 4.2), forward=False)
        #plt.show()
        plt.savefig("Graphs/paper/"+INPUT_FOLDER+"_diamerr_graph.png",bbox_inches='tight',pad_inches=0.01)
