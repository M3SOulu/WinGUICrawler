#!/usr/bin/env python

#from __future__ import print_function
import sys
import os
import random

INPUT_FOLDER = sys.argv[1]
nodules = []
#walks the input directory and finds input images and their paths
for root, dirs, files in os.walk(INPUT_FOLDER):
    path = root.split(os.sep)
    for file in files:
        if file[-1] == "g" and file[-2]=="n" and file[-3]=="p":
            nodules.append(file)

random.shuffle(nodules)

i = 0
for nod in nodules:
    i+=1
    print("\\begin{center}")
    print("\\Large Nodule "+str(i))
    print("\\end{center}")
    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.9\\textwidth]{"+nod+"}")
    print("\\end{figure}")
    print("\\begin{Form}[]")
    print("    \\begin{tcolorbox}")
    print("    \\TextField[name=ap"+str(i)+",width=2cm]{Area preservation: \\hspace{1.06cm}}\\\\[2mm]")
    print("    \\TextField[name=sp"+str(i)+",width=2cm]{Shape preservation: \\hspace{0.86cm}}\\\\[2mm]")
    print("    \\TextField[name=od"+str(i)+",width=2cm]{Overall diagnostic quality: }")
    print("    \\end{tcolorbox}")
    print("\\end{Form}")
    if  i%2 != 0:
        print("\\vspace{1cm}")
        print("\\hrule")
    if i%2 == 0:
        print("\\pagebreak")
        print("\\hrule")
