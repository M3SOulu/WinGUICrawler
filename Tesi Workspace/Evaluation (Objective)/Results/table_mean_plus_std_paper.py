#!/usr/bin/env python
#from __future__ import print_function
import sys
import math
import numpy as np

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

print("\\begin{table}[h!]")
print("\\centering")
print("\\begin{tabular}{lcccccc}")
print("\\hline")
print("& \\multicolumn{3}{c}{Fast Marching Method} & \\multicolumn{3}{c}{Active Contours} \\\\ & IoU & e_{long-axis}[\%] & e_{short-axis}[\%]  & IoU & e_{long-axis}[\%] & e_{short-axis}[\%]  \\\\")
print("\\hline")

stringhette = ["Round","Semi-transparent","Cavitary","Irregular"]
for stringhetta in stringhette:
    stampina = ""

    INPUT_FOLDER = stringhetta#sys.argv[1]

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

    stampina += stringhetta+ " & " + str(np.mean(iou_fmm_array))[:5]+" \\pm \\: "+str(np.std(iou_fmm_array))[:5]+" "
    stampina += " & " + signif_str(np.mean(longerr_fmm_array))+" \\pm \\: "+signif_str(np.std(longerr_fmm_array))+" "
    stampina += " & " + signif_str(np.mean(shorterr_fmm_array))+" \\pm \\: "+signif_str(np.std(shorterr_fmm_array))+" "
    stampina += " & " + str(np.mean(iou_ac_array))[:5]+" \\pm \\: "+str(np.std(iou_ac_array))[:5]+" "
    stampina += " & " + signif_str(np.mean(longerr_ac_array))+" \\pm \\: "+signif_str(np.std(longerr_ac_array))+" "
    stampina += " & " + signif_str(np.mean(shorterr_ac_array))+" \\pm \\: "+signif_str(np.std(shorterr_ac_array))+" \\\\"
    print(stampina)
    """print("IoU")
    print("FMM : ",str(np.mean(iou_fmm_array))," +/- ",str(np.std(iou_fmm_array)))
    print("AC : ",str(np.mean(iou_ac_array))," +/- ",str(np.std(iou_ac_array)))
    print("Long-axis")
    print("FMM : ",signif_str(np.mean(longerr_fmm_array))," +/- ",signif_str(np.std(longerr_fmm_array)))
    print("AC : ",signif_str(np.mean(longerr_ac_array))," +/- ",signif_str(np.std(longerr_ac_array)))
    print("Short-axis")
    print("FMM : ",signif_str(np.mean(shorterr_fmm_array))," +/- ",signif_str(np.std(shorterr_fmm_array)))
    print("AC : ",signif_str(np.mean(shorterr_ac_array))," +/- ",signif_str(np.std(shorterr_ac_array)))
    """
print("\\hline")
print("\end{tabular}")
print("\caption{Mean Std Obj}")
print("\label{mean_std_table_obj}")
print("\end{table}")

"""if INPUT_FOLDER[-1] == "/":
    INPUT_FOLDER = INPUT_FOLDER[:-1]"""

exit()
