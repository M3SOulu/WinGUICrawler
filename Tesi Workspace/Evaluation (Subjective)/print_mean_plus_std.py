#!/usr/bin/env python
#from __future__ import print_function
import sys
import math
import numpy as np

"""def signif_str(x):
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
    return s"""

#stringhette = ["Round","Semi-transparent","Cavitary","Irregular"]
#for stringhetta in stringhette:

INPUT_FOLDER = sys.argv[1] #stringhetta

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
    fmmap.append(float(s[1].split(":")[-1]))
    fmmsp.append(float(s[2].split(":")[-1]))
    fmmod.append(float(s[3].split(":")[-1]))
    acap.append(float(s[4].split(":")[-1]))
    acsp.append(float(s[5].split(":")[-1]))
    acod.append(float(s[6].split(":")[-1]))
fmmap_array = np.array(fmmap)
fmmsp_array = np.array(fmmsp)
fmmod_array = np.array(fmmod)
acap_array = np.array(acap)
acsp_array = np.array(acsp)
acod_array = np.array(acod)

print("Area preservation")
print("FMM : ",str(np.mean(fmmap_array))[:4]," \\pm \\: ",str(np.std(fmmap_array))[:4])
print("AC : ",str(np.mean(acap_array))[:4]," \\pm \\: ",str(np.std(acap_array))[:4])
print("Shape preservation")
print("FMM : ",str(np.mean(fmmsp_array))[:4]," \\pm \\: ",str(np.std(fmmsp_array))[:4])
print("AC : ",str(np.mean(acsp_array))[:4]," \\pm \\: ",str(np.std(acsp_array))[:4])
print("Overall diagnostic quality")
print("FMM : ",str(np.mean(fmmod_array))[:4]," \\pm \\: ",str(np.std(fmmod_array))[:4])
print("AC : ",str(np.mean(acod_array))[:4]," \\pm \\: ",str(np.std(acod_array))[:4])

if INPUT_FOLDER[-1] == "/":
    INPUT_FOLDER = INPUT_FOLDER[:-1]

exit()
