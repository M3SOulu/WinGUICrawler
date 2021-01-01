import PyPDF2 as pypdf
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import statistics

class nodule:
    def __init__(self,index,name,type,ap,sp,od):
        self.index = index
        self.name = name
        self.type = type
        self.ap = ap
        self.sp = sp
        self.od = od

    def __str__(self):
        return "index: "+str(self.index)+"| name: "+str(self.name)+"| type: "+str(self.type)+"| ap: "+str(self.ap)+"| sp: "+str(self.sp)+"| od: "+str(self.od)

INPUT_FILE_FORM_1 = sys.argv[1]
INPUT_FILE_FORM_2 = sys.argv[2]
INPUT_FILE_FORM_3 = sys.argv[3]
INPUT_FILE_FORM_4 = sys.argv[4]
INPUT_FILE_FORM_5 = sys.argv[5]
INPUT_FILE_TXT_INDICES = sys.argv[6]

pdfobject_1=open(INPUT_FILE_FORM_1,'rb')
pdfobject_2=open(INPUT_FILE_FORM_2,'rb')
pdfobject_3=open(INPUT_FILE_FORM_3,'rb')
pdfobject_4=open(INPUT_FILE_FORM_4,'rb')
pdfobject_5=open(INPUT_FILE_FORM_5,'rb')
pdf_1=pypdf.PdfFileReader(pdfobject_1)
pdf_2=pypdf.PdfFileReader(pdfobject_2)
pdf_3=pypdf.PdfFileReader(pdfobject_3)
pdf_4=pypdf.PdfFileReader(pdfobject_4)
pdf_5=pypdf.PdfFileReader(pdfobject_5)
form_1 = (pdf_1.getFormTextFields())
form_2 = (pdf_2.getFormTextFields())
form_3 = (pdf_3.getFormTextFields())
form_4 = (pdf_4.getFormTextFields())
form_5 = (pdf_5.getFormTextFields())

index = 1
nodule_list = []
f = open(INPUT_FILE_TXT_INDICES)
for x in f:
    if "LIDC" in x:
        y = x[38:len(x)-2]
        if "fmm" in y:
            t = "fmm"
            y = y[:len(y)-16]
        if "ac" in y:
            t = "ac"
            y = y[:len(y)-15]
        ap = str(statistics.mean([int(form_1.get("ap"+str(index))),int(form_2.get("ap"+str(index))),int(form_3.get("ap"+str(index))),int(form_4.get("ap"+str(index))),int(form_5.get("ap"+str(index)))]))
        sp = str(statistics.mean([int(form_1.get("sp"+str(index))),int(form_2.get("sp"+str(index))),int(form_3.get("sp"+str(index))),int(form_4.get("sp"+str(index))),int(form_5.get("sp"+str(index)))]))
        od = str(statistics.mean([int(form_1.get("od"+str(index))),int(form_2.get("od"+str(index))),int(form_3.get("od"+str(index))),int(form_4.get("od"+str(index))),int(form_5.get("od"+str(index)))]))
        nodule_list.append(nodule(index,y,t,ap,sp,od))
        index+=1

total_nodules = int(len(nodule_list)/2)
fmm_ap = np.zeros(total_nodules)
fmm_sp = np.zeros(total_nodules)
fmm_od = np.zeros(total_nodules)
ac_ap= np.zeros(total_nodules)
ac_sp= np.zeros(total_nodules)
ac_od = np.zeros(total_nodules)
x = np.arange(total_nodules)
final_index = 0
for nodfmm in nodule_list:
    if(nodfmm.type) == "fmm":
        for nodac in nodule_list:
            if nodac.type == "ac" and nodfmm.name == nodac.name:
                fmm_ap[final_index] = nodfmm.ap
                fmm_sp[final_index] = nodfmm.sp
                fmm_od[final_index] = nodfmm.od
                ac_ap[final_index] = nodac.ap
                ac_sp[final_index] = nodac.sp
                ac_od[final_index] = nodac.od
                #print(final_index,"-",nodfmm.name,".....index-fmm: "+str(nodfmm.index)+" | index-ac: "+str(nodac.index))
                final_index+=1
                print(nodfmm.name+"&"+"fmmap:"+nodfmm.ap+"&"+"fmmsp:"+nodfmm.sp+"&"+"fmmod:"+nodfmm.od+"&"+"acap:"+nodac.ap+"&"+"acsp:"+nodac.sp+"&"+"acod:"+nodac.od)
mean_fmm_ap = round(np.mean(fmm_ap),2)
mean_ac_ap = round(np.mean(ac_ap),2)
mean_fmm_sp = round(np.mean(fmm_sp),2)
mean_ac_sp = round(np.mean(ac_sp),2)
mean_fmm_od = round(np.mean(fmm_od),2)
mean_ac_od = round(np.mean(ac_od),2)
"""
print("Area preservation: fmm_mean = "+str(mean_fmm_ap)+" ac_mean = "+str(mean_ac_ap))
print("Shape preservation: fmm_mean = "+str(mean_fmm_sp)+" ac_mean = "+str(mean_ac_sp))
print("Overall Diagnostic Quality: fmm_mean = "+str(mean_fmm_od)+" ac_mean = "+str(mean_ac_od))
"""
fig,ax = plt.subplots(3)
ax[0].plot(x,fmm_ap,'r',label="fmm_ap")
ax[0].plot(x,ac_ap,'b',label="ac_ap")
ax[1].plot(x,fmm_sp,'r',label="fmm_sp")
ax[1].plot(x,ac_sp,'b',label="ac_sp")
ax[2].plot(x,fmm_od,'r',label="fmm_od")
ax[2].plot(x,ac_od,'b',label="ac_od")
red_patch = mpatches.Patch(color='red', label='FMM')
blue_patch = mpatches.Patch(color='blue', label='AC')
ax[0].legend(handles=[blue_patch,red_patch])
ax[1].legend(handles=[blue_patch,red_patch])
ax[2].legend(handles=[blue_patch,red_patch])
#ax.set_xlabel("nodule")
#ax.set_ylabel("IoU score")
ax[0].set_ylim([1,6])
ax[1].set_ylim([1,6])
ax[2].set_ylim([1,6])
ax[0].set_xlim([0,total_nodules-1])
ax[1].set_xlim([0,total_nodules-1])
ax[2].set_xlim([0,total_nodules-1])
ax[0].set_xticks(np.arange(0,total_nodules,1))
ax[1].set_xticks(np.arange(0,total_nodules,1))
ax[2].set_xticks(np.arange(0,total_nodules,1))
ax[0].set_title("Area preservation: fmm_mean = "+str(mean_fmm_ap)+" ac_mean = "+str(mean_ac_ap))
ax[1].set_title("Shape preservation: fmm_mean = "+str(mean_fmm_sp)+" ac_mean = "+str(mean_ac_sp))
ax[2].set_title("Overall Diagnostic Quality: fmm_mean = "+str(mean_fmm_od)+" ac_mean = "+str(mean_ac_od))
ax[0].set_yticks(np.arange(1,6,1))
ax[1].set_yticks(np.arange(1,6,1))
ax[2].set_yticks(np.arange(1,6,1))
fig.tight_layout(pad=1.0)
ax[0].grid()
ax[1].grid()
ax[2].grid()
#plt.show()
