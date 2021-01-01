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

#stringhette = ["Round","Semi-transparent","Cavitary","Irregular"]
#for stringhetta in stringhette:
INPUT_FOLDER = sys.argv[1]#stringhetta#

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
if INPUT_FOLDER[:4] == "Roun" or INPUT_FOLDER[:4] == "Irre" or  INPUT_FOLDER[:4] == "Semi":
    n = len(scores_list)
    mezzo = int(math.ceil(n/2))
    fmmap1 = fmmap[:mezzo]
    fmmap2 = fmmap[mezzo:]
    acap1 = acap[:mezzo]
    acap2 = acap[mezzo:]
    fmmsp1 = fmmsp[:mezzo]
    fmmsp2 = fmmsp[mezzo:]
    acsp1 = acsp[:mezzo]
    acsp2 = acsp[mezzo:]
    fmmod1 = fmmod[:mezzo]
    fmmod2 = fmmod[mezzo:]
    acod1 = acod[:mezzo]
    acod2 = acod[mezzo:]
    x1 = np.arange(1,mezzo+1,1)
    x2 = np.arange(mezzo+1,n+1,1)

    width1 = np.min(np.diff(x1))/3
    width2 = np.min(np.diff(x2))/3

    fig,ax = plt.subplots(1,1)
    ax.bar(x1+width1/2,acap1,width1,color='b',label='-Ymin')
    ax.bar(x1-width1/2,fmmap1,width1,color='r',label='Ymax')
    ax.set_xlim((1-2*width1, mezzo+2*width1))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x1)
    ax.set_ylabel("Area preservation",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_area_preservation_graph1.png",bbox_inches='tight',pad_inches=0.01)
    plt.show()
    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_area_preservation_graph1.png}")
    print("\\caption{"+INPUT_FOLDER+" - Area preservation}")
    print("\\label{fig:"+INPUT_FOLDER+"_area_preservation_graph1}")
    print("\\end{figure}")
    print("")

    fig,ax = plt.subplots(1,1)
    ax.bar(x2+width2/2,acap2,width2,color='b',label='-Ymin')
    ax.bar(x2-width2/2,fmmap2,width2,color='r',label='Ymax')
    ax.set_xlim((mezzo+1-2*width2, n+2*width2))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x2)
    ax.set_ylabel("Area preservation",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_area_preservation_graph2.png",bbox_inches='tight',pad_inches=0.01)
    plt.show()
    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_area_preservation_graph2.png}")
    print("\\caption{"+INPUT_FOLDER+" - Area preservation}")
    print("\\label{fig:"+INPUT_FOLDER+"_area_preservation_graph2}")
    print("\\end{figure}")
    print("")

    fig,ax = plt.subplots(1,1)
    ax.bar(x1+width1/2,acsp1,width1,color='b',label='-Ymin')
    ax.bar(x1-width1/2,fmmsp1,width1,color='r',label='Ymax')
    ax.set_xlim((1-2*width1, mezzo+2*width1))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x1)
    ax.set_ylabel("Shape preservation",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_shape_preservation_graph1",bbox_inches='tight',pad_inches=0.01)
    plt.show()

    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_shape_preservation_graph1.png}")
    print("\\caption{"+INPUT_FOLDER+" - Shape preservation}")
    print("\\label{fig:"+INPUT_FOLDER+"_shape_preservation_graph1}")
    print("\\end{figure}")
    print("")

    fig,ax = plt.subplots(1,1)
    ax.bar(x2+width2/2,acsp2,width2,color='b',label='-Ymin')
    ax.bar(x2-width2/2,fmmsp2,width2,color='r',label='Ymax')
    ax.set_xlim((mezzo+1-2*width2, n+2*width2))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x2)
    ax.set_ylabel("Shape preservation",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_shape_preservation_graph2",bbox_inches='tight',pad_inches=0.01)
    plt.show()

    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_shape_preservation_graph2.png}")
    print("\\caption{"+INPUT_FOLDER+" - Shape preservation}")
    print("\\label{fig:"+INPUT_FOLDER+"_shape_preservation_graph2}")
    print("\\end{figure}")
    print("")

    fig,ax = plt.subplots(1,1)
    ax.bar(x1+width1/2,acod1,width1,color='b',label='-Ymin')
    ax.bar(x1-width1/2,fmmod1,width1,color='r',label='Ymax')
    ax.set_xlim((1-2*width1, mezzo+2*width1))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x1)
    ax.set_ylabel("Overall diagnostic quality",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_overall_diag_qual_graph1.png",bbox_inches='tight',pad_inches=0.01)
    plt.show()

    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_overall_diag_qual_graph1}")
    print("\\caption{"+INPUT_FOLDER+" - Overall diagnostic quality}")
    print("\\label{fig:"+INPUT_FOLDER+"_overall_diag_qual_graph1}")
    print("\\end{figure}")
    print("")

    fig,ax = plt.subplots(1,1)
    ax.bar(x2+width2/2,acod2,width2,color='b',label='-Ymin')
    ax.bar(x2-width2/2,fmmod2,width2,color='r',label='Ymax')
    ax.set_xlim((mezzo+1-2*width1, n+2*width2))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x2)
    ax.set_ylabel("Overall diagnostic quality",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_overall_diag_qual_graph2.png",bbox_inches='tight',pad_inches=0.01)
    plt.show()

    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_overall_diag_qual_graph2}")
    print("\\caption{"+INPUT_FOLDER+" - Overall diagnostic quality}")
    print("\\label{fig:"+INPUT_FOLDER+"_overall_diag_qual_graph2}")
    print("\\end{figure}")
    print("")

else:

    n = len(scores_list)
    x = np.arange(1,n+1,1)
    #Calculate optimal width
    width = np.min(np.diff(x))/3

    fig,ax = plt.subplots(1,1)
    ax.bar(x+width/2,acap,width,color='b',label='-Ymin')
    ax.bar(x-width/2,fmmap,width,color='r',label='Ymax')
    ax.set_xlim((1-2*width, n+2*width))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x)
    ax.set_ylabel("Area preservation",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_area_preservation_graph.png",bbox_inches='tight',pad_inches=0.01)
    plt.show()

    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_area_preservation_graph.png}")
    print("\\caption{"+INPUT_FOLDER+" - Area preservation}")
    print("\\label{fig:"+INPUT_FOLDER+"_area_preservation_graph}")
    print("\\end{figure}")
    print("")

    fig,ax = plt.subplots(1,1)
    ax.bar(x+width/2,acsp,width,color='b',label='-Ymin')
    ax.bar(x-width/2,fmmsp,width,color='r',label='Ymax')
    ax.set_xlim((1-2*width, n+2*width))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x)
    ax.set_ylabel("Shape preservation",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_shape_preservation_graph",bbox_inches='tight',pad_inches=0.01)
    plt.show()
    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_shape_preservation_graph.png}")
    print("\\caption{"+INPUT_FOLDER+" - Shape preservation}")
    print("\\label{fig:"+INPUT_FOLDER+"_shape_preservation_graph}")
    print("\\end{figure}")
    print("")

    fig,ax = plt.subplots(1,1)
    ax.bar(x+width/2,acod,width,color='b',label='-Ymin')
    ax.bar(x-width/2,fmmod,width,color='r',label='Ymax')
    ax.set_xlim((1-2*width, n+2*width))
    ax.set_ylim((0.5, 5.5))
    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks(x)
    ax.set_ylabel("Overall diagnostic quality",fontsize=16)
    ax.set_xlabel("Index",fontsize=16)
    red_patch = mpatches.Patch(color='red', label='FMM')
    blue_patch = mpatches.Patch(color='blue', label='AC')
    ax.legend(handles=[blue_patch,red_patch])
    ax.grid(axis='y',color='k', linestyle='dashed')

    #plt.savefig("Graphs/"+INPUT_FOLDER+"_overall_diag_qual_graph.png",bbox_inches='tight',pad_inches=0.01)
    plt.show()
    print("\\begin{figure}[h!]")
    print("\\centering")
    print("\\includegraphics[width=0.86\linewidth]{img/"+INPUT_FOLDER+"_overall_diag_qual_graph}")
    print("\\caption{"+INPUT_FOLDER+" - Overall diagnostic quality}")
    print("\\label{fig:"+INPUT_FOLDER+"_overall_diag_qual_graph}")
    print("\\end{figure}")
    print("")
