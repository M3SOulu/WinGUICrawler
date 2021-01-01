#!/usr/bin/env python
#from __future__ import print_function
import sys
import math

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

#stringhette = ["Round","Semi-transparent","Cavitary","Irregular"]
#for stringhetta in stringhette:

INPUT_FOLDER = sys.argv[1] #stringhetta

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

print("\\begin{table}[h!]  \\label{"+INPUT_FOLDER+"\\_obj\\_table} ")
print("\\begin{tabular}{p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|}")
print("\\cline{2-7}")
print("& \\multicolumn{2}{p{3cm}|}{\\phantom{rt-ax[]}IoU\\phantom{is\\_err\\%}} & \\multicolumn{2}{l|}{Long-axis err.[\\%]\\phantom{.}} & \\multicolumn{2}{l|}{Short-axis err.[\\%]} \\\\ \\hline")
print("\\multicolumn{1}{|p{1.5cm}|}{Index} & FMM         & AC\\phantom{M}         & FMM               & AC\\phantom{M}              & FMM               & AC\\phantom{M}               \\\\ \\hline")
for i in range(1,n+1):
    print( "\\multicolumn{1}{|c|}{"+str(i)+"}"+"&"+signif_str(iou_fmm[i-1])+"&"+signif_str(iou_ac[i-1])+"&"+signif_str(longerr_fmm[i-1])+"&"+signif_str(longerr_ac[i-1])+"&"+signif_str(shorterr_fmm[i-1])+"&"+signif_str(shorterr_ac[i-1])+"\\\\ \\hline")
print("\\end{tabular}")
print("\\caption{"+INPUT_FOLDER+" objective evaluation results}")
print("\\end{table}")
exit()
