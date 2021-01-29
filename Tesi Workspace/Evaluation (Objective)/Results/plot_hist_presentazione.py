#!/usr/bin/env python
#from __future__ import print_function
import sys
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator,PercentFormatter)


def signif_str(x):
    s = "{0:.3g}".format(x)
    str(s)
    if x < 1:
        f1 = False
        f2 = False
        counter = 0
        for i in range(0,len(s)):
            if(s[i]) == ".":
                f1 = True
            if f1 == True:
                if (s[i] != "0") and (s[i] != ".") and ((s[i-1] == "0") or (s[i-1] == ".")):
                    f2 = True
            if f1 == True and f2 == True:
                counter += 1
        diff = 3 - counter
        if diff == 1:
            s = s + "0"
        if diff == 2:
            s = s + "00"
    else:
        diff = 3 - len(s.replace('.', ''))
        if diff == 1:
            if "." in s:
                s = s + "0"
            else:
                s = s + ".0"
        if diff == 2:
            if "." in s:
                s = s + "00"
            else:
                s = s + ".00"
    return s

iou_fmm_mean_list = []
iou_fmm_std_list = []
iou_ac_mean_list = []
iou_ac_std_list = []

stringhette = ["Round","Irregular","Semi-transparent","Cavitary"]
for stringhetta in stringhette:
    INPUT_FOLDER = stringhetta#sys.argv[1] #stringhetta
    if INPUT_FOLDER[-1] == "/":
        INPUT_FOLDER = INPUT_FOLDER[:-1]

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
    n = len(scores_list)
    for s in scores_list:
        iou_fmm.append(float(s[1]))
        iou_ac.append(float(s[4]))
        longerr_fmm.append(float(s[2]))
        longerr_ac.append(float(s[5]))
        shorterr_fmm.append(float(s[3]))
        shorterr_ac.append(float(s[6]))
    if INPUT_FOLDER[-1] == "/":
        INPUT_FOLDER = INPUT_FOLDER[:-1]

    iou_fmm_array = np.array(iou_fmm)
    iou_ac_array = np.array(iou_ac)
    longerr_fmm_array = np.array(longerr_fmm)
    longerr_ac_array = np.array(longerr_ac)
    shorterr_fmm_array = np.array(shorterr_fmm)
    shorterr_ac_array = np.array(shorterr_ac)


    iou_fmm_mean = float(str(np.mean(iou_fmm_array))[:5])
    iou_fmm_std = float(str(np.std(iou_fmm_array))[:5])
    iou_ac_mean = float(str(np.mean(iou_ac_array))[:5])
    iou_ac_std = float(str(np.std(iou_ac_array))[:5])

    longerr_fmm_mean = float(signif_str(np.mean(longerr_fmm_array)))
    longerr_fmm_std = float(signif_str(np.std(longerr_fmm_array)))
    longerr_ac_mean = float(signif_str(np.mean(longerr_ac_array)))
    longerr_ac_std = float(signif_str(np.std(longerr_ac_array)))

    shorterr_fmm_mean = float(signif_str(np.mean(shorterr_fmm_array)))
    shorterr_fmm_std = float(signif_str(np.std(shorterr_fmm_array)))
    shorterr_ac_mean = float(signif_str(np.mean(shorterr_ac_array)))
    shorterr_ac_std = float(signif_str(np.std(shorterr_ac_array)))

    err_ac_mean = [longerr_ac_mean,shorterr_ac_mean]
    err_fmm_mean = [longerr_fmm_mean,shorterr_fmm_mean]
    err_ac_std = [longerr_ac_std,shorterr_ac_std]
    err_fmm_std = [longerr_fmm_std,shorterr_fmm_std]

    iou_fmm_mean_list.append(iou_fmm_mean)
    iou_fmm_std_list.append(iou_fmm_std)
    iou_ac_mean_list.append(iou_ac_mean)
    iou_ac_std_list.append(iou_ac_std)


fig,ax = plt.subplots(1,1)
x = np.arange(1,5,1)
#Calculate optimal width
width = np.min(np.diff(x))/4

xlabels = ['Round', 'Irregular', 'Semi-trans.','Cavitary']

ax.bar(x+width/2,iou_ac_mean_list,width,color='b',yerr=iou_ac_std_list,align='center', ecolor='darkblue', capsize=8)
ax.bar(x-width/2,iou_fmm_mean_list,width,color='r',yerr=iou_fmm_std_list,align='center', ecolor='darkred', capsize=8)

ax.set_ylabel("Intersection over Union")
ax.set_xlim((1-2*width, 4+2*width))
ax.set_xticks(x)
ax.set_xticklabels(xlabels)
red_patch = mpatches.Patch(color='red', label='FMM')
blue_patch = mpatches.Patch(color='blue', label='AC')
ax.legend(handles=[blue_patch,red_patch])
ax.grid(axis='y',color='k', linestyle='dashed')
#plt.savefig("Hist/"+"hist.png",bbox_inches='tight',pad_inches=0.01)
plt.show()


exit()
