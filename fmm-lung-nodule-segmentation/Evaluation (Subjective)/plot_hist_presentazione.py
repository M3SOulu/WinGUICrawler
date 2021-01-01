#!/usr/bin/env python
#from __future__ import print_function
import sys
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator,PercentFormatter)

fmm_mean_list = []
fmm_std_list = []
ac_mean_list = []
ac_std_list = []

stringhette = ["Round","Irregular","Semi-transparent","Cavitary"]
for stringhetta in stringhette:

    INPUT_FOLDER = stringhetta #sys.argv[1] #stringhetta
    if INPUT_FOLDER[-1] == "/":
        INPUT_FOLDER = INPUT_FOLDER[:-1]

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
    n = len(scores_list)
    for s in scores_list:
        fmmap.append(int(s[1].split(":")[-1]))
        fmmsp.append(int(s[2].split(":")[-1]))
        fmmod.append(int(s[3].split(":")[-1]))
        acap.append(int(s[4].split(":")[-1]))
        acsp.append(int(s[5].split(":")[-1]))
        acod.append(int(s[6].split(":")[-1]))
    fmmap_array = np.array(fmmap)
    fmmsp_array = np.array(fmmsp)
    fmmod_array = np.array(fmmod)
    acap_array = np.array(acap)
    acsp_array = np.array(acsp)
    acod_array = np.array(acod)

    fmm_array = (fmmap_array+fmmsp_array+fmmod_array)/3
    ac_array = (acap_array+acsp_array+acod_array)/3

    fmm_mean = float(str(np.mean(fmm_array))[:4])
    fmm_std = float(str(np.std(fmm_array))[:4])
    ac_mean = float(str(np.mean(ac_array))[:4])
    ac_std = float(str(np.std(ac_array))[:4])
    fmm_mean_list.append(fmm_mean)
    fmm_std_list.append(fmm_std)
    ac_mean_list.append(ac_mean)
    ac_std_list.append(ac_std)


#-----------------------------------------------------------

x = np.arange(1,5,1)
#Calculate optimal width
width = np.min(np.diff(x))/4

xlabels = ['Round', 'Irregular', 'Semi-trans.','Cavitary']
fig,ax = plt.subplots(1,1)
ax.bar(x+width/2,ac_mean_list,width,color='b',yerr=ac_std_list,align='center', ecolor='darkblue', capsize=8)
ax.bar(x-width/2,fmm_mean_list,width,color='r',yerr=fmm_std_list,align='center', ecolor='darkred', capsize=8)

ax.set_ylabel("Mean opinion score")
ax.set_xlim((1-2*width, 4+2*width))
ax.set_ylim((1, 6))
ax.set_yticks([1,2,3,4,5])
ax.set_xticks(x)
ax.set_xticklabels(xlabels)
red_patch = mpatches.Patch(color='red', label='FMM')
blue_patch = mpatches.Patch(color='blue', label='AC')
ax.legend(handles=[blue_patch,red_patch])
ax.grid(axis='y',color='k', linestyle='dashed')
#plt.savefig("Hist/"+"hist.png",bbox_inches='tight',pad_inches=0.01)
plt.show()

exit()
