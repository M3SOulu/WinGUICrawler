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
    INPUT_FOLDER = stringhetta #sys.argv[1]

    scores_list = []
    fmmap = []
    fmmsp = []
    fmmod = []
    acap = []
    acsp = []
    acod = []

    scores = open(INPUT_FOLDER+"/scores.txt")
    for f in scores:
        scores_list.append(f[:-1].split("&"))
    scores_list.sort()

    for s in scores_list:
        fmmap.append(float(s[1].split(":")[-1]))
        fmmsp.append(float(s[2].split(":")[-1]))
        fmmod.append(float(s[3].split(":")[-1]))
        acap.append(float(s[4].split(":")[-1]))
        acsp.append(float(s[5].split(":")[-1]))
        acod.append(float(s[6].split(":")[-1]))

    if INPUT_FOLDER[-1] == "/":
        INPUT_FOLDER = INPUT_FOLDER[:-1]
    plt_scale = 1
    if INPUT_FOLDER[:4] == "Roun" or INPUT_FOLDER[:4] == "Irre" or  INPUT_FOLDER[:4] == "Semi":
        plt_scale = 2
    n = len(scores_list)
    x = np.arange(1,n+1,1)
    #Calculate optimal width
    width = np.min(np.diff(x))/8

    fig,ax = plt.subplots(1,1)
    fig.set_size_inches((5.5*plt_scale, 4.2), forward=False)
    ax.bar(x-2.5*width,fmmap,width,color='cyan')
    ax.bar(x-1.5*width,fmmsp,width,color='royalblue')
    ax.bar(x-0.5*width,fmmod,width,color='darkblue')
    ax.bar(x+0.5*width,acap,width,color='salmon')
    ax.bar(x+1.5*width,acsp,width,color='firebrick')
    ax.bar(x+2.5*width,acod,width,color='maroon')

    ax.set_xlim((1-4*width, n+4*width))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x)
    ax.set_ylabel("Mean Opinion Score",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    salmon_patch = mpatches.Patch(color='salmon', label='Area pres. - AC')
    firebrick_patch = mpatches.Patch(color='firebrick', label='Shape pres. - AC')
    maroon_patch = mpatches.Patch(color='maroon', label='Overall diag. qual. - AC')
    cyan_patch = mpatches.Patch(color='cyan', label='Area pres. - FMM')
    royalblue_patch = mpatches.Patch(color='royalblue', label='Shape pres. - FMM')
    darkblue_patch = mpatches.Patch(color='darkblue', label='Overall diag. qual. - FMM')
    legend_pos = 0.48
    if plt_scale == 1:
        legend_pos = 0.08
    ax.legend(bbox_to_anchor=(legend_pos, 0.9),handles=[cyan_patch,royalblue_patch,darkblue_patch,salmon_patch,firebrick_patch,maroon_patch],ncol=2)
    ax.grid(axis='y',color='k', linestyle=(0, (5, 10)))
    plt.savefig("Graphs/"+INPUT_FOLDER+"_mos_graph.png",bbox_inches='tight',pad_inches=0.01)
    #plt.show()
    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_mos_graph.png}")
    print("\\caption{"+INPUT_FOLDER+" - Mean opinion score }")
    print("\\label{fig:"+INPUT_FOLDER+"_mos_graph}")
    print("\\end{figure}")
    print("")
