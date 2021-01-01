#!/usr/bin/env python
#from __future__ import print_function
import sys
import math

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

if INPUT_FOLDER[-1] == "/":
    INPUT_FOLDER = INPUT_FOLDER[:-1]

print("\\begin{table}[h!]  \\label{"+INPUT_FOLDER+"\\_sub\\_table} ")
print("\\begin{tabular}{p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|}")
print("\\cline{2-7}")
print("& \\multicolumn{2}{p{3cm}|}{Area preservation} & \\multicolumn{2}{l|}{Shape preservation} & \\multicolumn{2}{l|}{Overall diag. qual.} \\\\ \\hline")
print("\\multicolumn{1}{|p{1.5cm}|}{Index} & FMM         & AC\\phantom{M}         & FMM               & AC\\phantom{M}              & FMM               & AC\\phantom{M}               \\\\ \\hline")
for i in range(1,n+1):
    print( "\\multicolumn{1}{|c|}{"+str(i)+"}"+"&"+str(fmmap[i-1])+"&"+str(acap[i-1])+"&"+str(fmmsp[i-1])+"&"+str(acsp[i-1])+"&"+str(fmmod[i-1])+"&"+str(acod[i-1])+"\\\\ \\hline")
print("\\end{tabular}")
print("\\caption{"+INPUT_FOLDER+" subjective evaluation results}")
print("\\end{table}")
exit()
