import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import pickle
import imageio
from scipy.ndimage import binary_dilation
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import PercentFormatter
from math import log10,floor
from  scipy import ndimage
from skimage import measure
from math import pi
import warnings
import operator

def round_sig(x, sig=3):
    return round(x, sig-int(floor(log10(abs(x))))-1)

def slope(point1,point2):
    if (point1[1]-point2[1]) != 0:
        return (point1[0]-point2[0])/(point1[1]-point2[1])
    else:
        return np.inf

def inv_slope(schlope):
    if schlope == np.inf:
        return 0
    if schlope == 0:
        return np.inf
    else:
        return -1/schlope

def length_measures(input_image,rescale_factor):  #Calculates major and minor axis with 2 methods
    measurements = [] #list of measures to be returned at the end
    label_img = measure.label(input_image)   #To get the ellipse the regionprops method is used

    label_img = ndimage.morphology.binary_fill_holes(label_img).astype(int)
    size = input_image.shape[0]
    if (np.all(label_img==0)):
        #print("FAILED COMPLETELY")
        measurements.append((0, np.array([0,0]), np.array([0,0]),"major_axis_ellipse"))
        measurements.append((0, np.array([0,0]), np.array([0,0]),"minor_axis_ellipse"))
        measurements.append((0, np.array([0,0]), np.array([0,0]),"major_axis"))
        measurements.append((0, np.array([0,0]), np.array([0,0]),"minor_axis"))
        return measurements

    regions = measure.regionprops(label_img)

    """fig,ax = plt.subplots(1,2)
    ax[0].imshow(label_img)
    ax[1].imshow(regions[0].filled_image)


    plt.suptitle(str(major_axis)+" - "+str(minor_axis))"""
    major_axis = round(regions[0].major_axis_length,2)
    minor_axis = round(regions[0].minor_axis_length,2)
    theta = -regions[0].orientation
    centroid = regions[0].centroid

    #An ellipse centered in the origin with the right axis leghts is created
    u = centroid[1];
    v = centroid[0];

    a = major_axis/2;
    b = minor_axis/2;
    t = np.linspace(0, 2*pi, 1000)
    x = a*np.cos(t)
    y = b*np.sin(t)
    xy = np.array([x,y,np.ones(1000,)])

    #Then by using a homogenous transformation matrix it is rotates by the ellipse orientation and translated by the centroid coords
    RT = np.array([[np.cos(theta),-np.sin(theta),u],[np.sin(theta),np.cos(theta),v],[0,0,1]])

    for num in range(1000):
        xy[:,num] = np.inner(RT,xy[:,num])

    x = xy[0]
    y = xy[1]

    measurements.append((round(major_axis*rescale_factor,1),np.array([int(round(y[0])),int(round(x[0]))]),np.array([int(round(y[500])),int(round(x[500]))]),"major_axis_ellipse"))
    measurements.append((round(minor_axis*rescale_factor,1),np.array([int(round(y[250])),int(round(x[250]))]),np.array([int(round(y[750])),int(round(x[750]))]),"minor_axis_ellipse"))

    borderu = input_image-ndimage.morphology.binary_erosion(input_image)  #finds border pixels by subtracting eroded image
    #plt.imshow(borderu)
    where = np.where(borderu == 1)

    #crates a list with all border pointsS
    bp_list =[]
    lenbp = len(where[0])
    for i in range(lenbp):
        bp = np.array([where[0][i],where[1][i]])
        bp_list.append(bp)

    #finds the furthest bordering pixel from the centroid, it will be the first point of major_axis
    max_dist = 0
    mp = np.array([0,0])
    mean = np.array([centroid[0],centroid[1]])
    for bp in bp_list:
        dist = np.linalg.norm(bp-mean)
        if (dist > max_dist):
            max_dist = dist
            mp = bp

    #finds the furthest bordering pixel from the first point, it will be the second point of major_axis
    max_dist_2 = 0
    mp2 = mp.copy()
    for bp in bp_list:
        dist = np.linalg.norm(bp-mp)
        if (dist > max_dist_2 ):
            mp2 = bp
            max_dist_2 = dist

    measurements.append((round(max_dist_2*rescale_factor,2),np.array([mp[0],mp[1]]),np.array([mp2[0],mp2[1]]),"major_axis"))
    #Using the line connecting the 2 major_axis points, the border points are divided in 2 sets

    major_axis_slope = slope(mp,mp2)
    major_axis_perp_slope = inv_slope(major_axis_slope)
    #print(major_axis_slope)
    #print(major_axis_perp_slope)

    """plt.imshow(borderu,cmap="gray")
    plt.axis("off")
    plt.plot(centroid[1],centroid[0],'yo')   #draw lines
    plt.plot(mp[1],mp[0],'ro')   #draw lines
    plt.plot([centroid[1],mp[1]],[centroid[0],mp[0]],'y')   #draw lines
    plt.plot(mp2[1],mp2[0],'ro')   #draw lines
    plt.plot([mp2[1],mp[1]],[mp2[0],mp[0]],'r')   #draw lines
    plt.show()
    exit()"""
    perp_list = []
    for p in bp_list:
        if not ((p[0] == mp2[0] and p[1] == mp2[1]) or (p[0] == mp[0] and p[1] == mp[1])):
            perp_list.append(p)

    perp_lines_list = []
    for pa in perp_list:
        perp_point = np.array([-1,-1])
        perp_slope = slope(pa,perp_point)
        for pb in perp_list:
            if not (pb[0] == pa[0] and pb[1] == pa[1]):
                if major_axis_perp_slope < np.inf:
                    temp_slope = slope(pa,pb)
                    diff_temp = np.abs(temp_slope-major_axis_perp_slope)
                    perp_slope = slope(pa,perp_point)
                    diff_perp= np.abs(perp_slope-major_axis_perp_slope)
                    if diff_temp < diff_perp and np.sign(temp_slope) == np.sign(major_axis_perp_slope):
                        perp_point = pb
                else:
                    if pa[1] == pb[1] and pa[1] != pb[0] and pa[0] != pb[1]:
                        perp_point = pb
        if perp_slope < np.inf and major_axis_perp_slope < np.inf:
            tan_alpha  = np.abs((major_axis_perp_slope-perp_slope)/(1+major_axis_perp_slope*perp_slope))
        else:
            tan_alpha = 0
        if tan_alpha < 0.15 and perp_point[0] != -1 and perp_point[1] != -1:
            perp_lines_list.append((round(np.linalg.norm(pa-perp_point),2),pa,perp_point))
    perp_lines_list.sort(key = operator.itemgetter(0))

    """plt.imshow(borderu,cmap="gray")
    plt.axis("off")
    plt.plot([mp[1], mp2[1]],[mp[0], mp2[0]],'r')   #draw lines
    plt.plot([mp[1], mp2[1]],[mp[0], mp2[0]],'ro')   #draw lines
    #for line in perp_lines_list:
    #    plt.plot([line[1][1], line[2][1]],[line[1][0], line[2][0]],'y')   #draw lines
    #    plt.plot([line[1][1], line[2][1]],[line[1][0], line[2][0]],'yo')   #draw lines
    plt.plot([perp_lines_list[-1][1][1], perp_lines_list[-1][2][1]],[perp_lines_list[-1][1][0], perp_lines_list[-1][2][0]],'b')
    plt.plot([perp_lines_list[-1][1][1], perp_lines_list[-1][2][1]],[perp_lines_list[-1][1][0], perp_lines_list[-1][2][0]],'bo')
    plt.show()
    exit()"""
    measurements.append((round(perp_lines_list[-1][0]*rescale_factor,2),perp_lines_list[-1][1],perp_lines_list[-1][2],"minor_axis"))

    #fig, ax  = plt.subplots(1,1)
    #plt.title("Ellipse Axis = "+str(measurements[0][0])+"mm & "+str(measurements[1][0])+"mm"+"\n"+" Axis = "+str(measurements[2][0])+"mm & "+str(measurements[3][0])+"mm")
    """plt.figtext(0.30, 0.915, "Ellipse Axis = "+str(measurements[0][0])+"mm & "+str(measurements[1][0])+"mm", fontsize='large', color='r', va ='top', ha = 'left')
    plt.figtext(0.34, 0.915, " Axis = "+str(measurements[2][0])+"mm & "+str(measurements[3][0])+"mm", fontsize='large', color='g', va ='bottom', ha = 'left')
    plt.imshow(input_image,cmap="gray")
    plt.plot( x,y,'r',linestyle='dashed') #draw ellipse
    plt.plot([x[0], x[250], x[500], x[750]], [y[0], y[250], y[500], y[750]], 'ro')  #draw points
    plt.plot([x[0], x[500]],[y[0], y[500]],'r')   #draw lines
    plt.plot([x[250], x[750]],[y[250], y[750]],'r')
    plt.plot((mp[1],mp2[1]),(mp[0],mp2[0]),'g')
    plt.plot((mp[1],mp2[1]),(mp[0],mp2[0]),'go')
    plt.axis("off")
    plt.plot((perp_lines_list[-1][1][1],perp_lines_list[-1][2][1]),(perp_lines_list[-1][1][0],perp_lines_list[-1][2][0]),'g')
    plt.plot((perp_lines_list[-1][1][1],perp_lines_list[-1][2][1]),(perp_lines_list[-1][1][0],perp_lines_list[-1][2][0]),'go')
    plt.show()"""
    return measurements


def IoU(segmented_image,GT):     #Calculates intersection over Union of segmentation results and ground truth
    intersection = np.multiply(segmented_image,groundtruth_image)
    union = groundtruth_image+segmented_image-intersection
    iou = round(np.sum(intersection)/np.sum(union),3)
    """fig, ax = plt.subplots(1,5)
    plt.suptitle("IoU score : "+str(iou), y=0.72)
    ax[0].axis('off')
    ax[0].set_title("Input")
    ax[1].axis('off')
    ax[1].set_title("GroundTruth")
    ax[2].axis('off')
    ax[2].set_title("Segmented")
    ax[3].axis('off')
    ax[3].set_title("Intersection")
    ax[4].axis('off')
    ax[4].set_title("Union")
    ax[0].imshow(input_image,cmap="gray")
    ax[1].imshow(groundtruth_image,cmap="gray")
    ax[2].imshow(segmented_image,cmap="gray")
    ax[3].imshow(intersection,cmap="gray")
    ax[4].imshow(union,cmap="gray")"""
    return iou

def double_ticks(x, pos):
    return int(x/2)

stringhette = ["Round","Irregular","Original","Cavitary","Semi-transparent"]
for stringhetta in stringhette:#walks the input directory and finds input images and their paths

    nodules = []
    INPUT_FOLDER = "Input_and_GroundTruth/Altered phantom nodules/"+stringhetta+"/Polygonal/10mm"

    index = 0
    for root, dirs, files in os.walk(INPUT_FOLDER):
        path = root.split(os.sep)
        for file in files:
            if file[-1] == "g" and file[-2]=="n" and file[-3]=="p" and file[-5] != "T" and file[-6] != "G":
                stringa = ""
                for p in path:
                    stringa+=p+"/"
                index += 1
                nodules.append((file,stringa,index))
    #reads and normalizes input image
    #major_axis_ellipse_list = []
    #minor_axis_ellipse_list = []
    major_axis_list_gt=[]
    minor_axis_list_gt=[]
    major_axis_list_fmm=[]
    minor_axis_list_fmm=[]
    major_axis_list_ac=[]
    minor_axis_list_ac=[]
    major_axis_err_list_fmm=[]
    minor_axis_err_list_fmm=[]
    major_axis_err_list_ac=[]
    minor_axis_err_list_ac=[]

    iou_list_ac = []
    iou_list_fmm = []
    print(stringhetta)
    for nod in nodules:
        """if nod[2] != 15:
            continue"""
        """print("------------------------------------------")
        print(nod)
        print("------------------------------------------")"""
        inputFilename = nod[1]+nod[0]
        input_image = imageio.imread(inputFilename)
        image_size = input_image.shape[0]
        if(len(input_image.shape)) > 2:
            input_image=input_image[:,:,:-1]              #These 3 lines are in case the image is a 4 channel png
            input_image = np.asarray(input_image)
            input_image = np.dot(input_image, [0.299, 0.587, 0.114])
        rescale_factor = 0.5

        groundtruth_image = imageio.imread(inputFilename[:-4]+"_GT.png")
        if(len(groundtruth_image.shape)) > 2:
            groundtruth_image=groundtruth_image[:,:,:-1]              #These 3 lines are in case the image is a 4 channel png
            groundtruth_image = np.asarray(groundtruth_image)
            groundtruth_image = np.dot(groundtruth_image, [0.299, 0.587, 0.114])
        groundtruth_image[groundtruth_image==255] = 1

        mask_fmm = imageio.imread("Segmented"+inputFilename[21:]+"_segmented.png")
        mask_ac = imageio.imread("Segmented_Matlab"+inputFilename[21:]+"_segmented.png")
        mask_ac[mask_ac==255] = 1
        mask_fmm[mask_fmm==255] = 1

        norm_input = (input_image - np.min(input_image))/(np.max(input_image)-np.min(input_image))

        Borderu_GT = binary_dilation(groundtruth_image)-groundtruth_image
        Borderu_GT = (255*Borderu_GT).astype(np.uint8)
        Borderu_FMM = binary_dilation(mask_fmm)-mask_fmm
        Borderu_FMM = (255*Borderu_FMM).astype(np.uint8)
        Borderu_AC = binary_dilation(mask_ac)-mask_ac
        Borderu_AC = (255*Borderu_AC).astype(np.uint8)

        rgb_img = np.stack((norm_input,)*3, axis=-1)
        rgb_img_GT = (255*rgb_img).astype(np.uint8)
        rgb_img_FMM = (255*rgb_img).astype(np.uint8)
        rgb_img_AC = (255*rgb_img).astype(np.uint8)

        bfmm = np.where(Borderu_FMM > 0)
        rgb_img_FMM[:,:,0][bfmm] = 255
        rgb_img_FMM[:,:,1][bfmm] = 0
        rgb_img_FMM[:,:,2][bfmm] = 0
        edgepixels = [0,image_size-1]
        for i in edgepixels:
            for j in range(image_size):
                if mask_ac[j,i] == 1:
                    Borderu_AC[j,i] = 255
                if mask_fmm[j,i] == 1:
                    Borderu_FMM[j,i] = 255
        for j in edgepixels:
            for i in range(image_size):
                if mask_ac[j,i] == 1:
                    Borderu_AC[j,i] = 255
                if mask_fmm[j,i] == 1:
                    Borderu_FMM[j,i] = 255

        bac = np.where(Borderu_AC > 0)
        rgb_img_AC[:,:,0][bac] = 0
        rgb_img_AC[:,:,1][bac] = 0
        rgb_img_AC[:,:,2][bac] = 255

        bgt = np.where(Borderu_GT > 0)
        rgb_img_GT[:,:,0][bgt] = 0
        rgb_img_GT[:,:,1][bgt] = 255
        rgb_img_GT[:,:,2][bgt] = 0

        tick_rate = 10
        if image_size > 78:
            tick_rate = 20
        if image_size < 32:
            tick_rate = 4
        measurements_gt = length_measures(groundtruth_image,rescale_factor)
        measurements_fmm = length_measures(mask_fmm,rescale_factor)
        measurements_ac = length_measures(mask_ac,rescale_factor)

        #major_axis_ellipse_list.append(measurements_gt[0][0])
        #minor_axis_ellipse_list.append(measurements_gt[1][0])

        major_axis_gt = round(measurements_gt[2][0],3)
        minor_axis_gt = round(measurements_gt[3][0],3)
        major_axis_fmm = round(measurements_fmm[2][0],3)
        minor_axis_fmm = round(measurements_fmm[3][0],3)
        major_axis_ac = round(measurements_ac[2][0],3)
        minor_axis_ac = round(measurements_ac[3][0],3)
        major_axis_list_gt.append(major_axis_gt)
        minor_axis_list_gt.append(minor_axis_gt)
        major_axis_list_fmm.append(major_axis_fmm)
        minor_axis_list_fmm.append(minor_axis_fmm)
        major_axis_list_ac.append(major_axis_ac)
        minor_axis_list_ac.append(minor_axis_ac)

        major_axis_err_list_fmm.append(round((abs(major_axis_fmm-major_axis_gt)/major_axis_gt)*100,3))
        minor_axis_err_list_fmm.append(round((abs(minor_axis_fmm-minor_axis_gt)/minor_axis_gt)*100,3))
        major_axis_err_list_ac.append(round((abs(major_axis_ac-major_axis_gt)/major_axis_gt)*100,3))
        minor_axis_err_list_ac.append(round((abs(minor_axis_ac-minor_axis_gt)/minor_axis_gt)*100,3))

        iou_list_fmm.append(IoU(mask_fmm,groundtruth_image))
        iou_list_ac.append(IoU(mask_ac,groundtruth_image))
        """fig,ax = plt.subplots(1,3)
        ax[0].imshow(rgb_img_GT,cmap="gray")
        ax[0].set_title("Ground Truth")
        ax[1].imshow(rgb_img_FMM)
        ax[2].set_xlabel("mm")
        ax[2].set_ylabel("mm")
        ax[1].set_xlabel("mm")
        ax[1].set_ylabel("mm")
        ax[0].set_xlabel("mm")
        ax[0].set_ylabel("mm")
        ax[2].imshow(rgb_img_AC,cmap="gray")
        ax[1].set_title("Fast Marching Method")
        ax[2].set_title("Active Contours")
        #ax[1].set_title(IoU(mask_fmm,groundtruth_image))
        #ax[2].set_title(IoU(mask_ac,groundtruth_image))

        #ax[0].plot([measurements_gt[2][1][1],measurements_gt[2][2][1],measurements_gt[3][1][1],measurements_gt[3][2][1]],[measurements_gt[2][1][0],measurements_gt[2][2][0],measurements_gt[3][1][0],measurements_gt[3][2][0]],'go')   #draw lines
        ax[0].plot([measurements_gt[2][1][1],measurements_gt[2][2][1]],[measurements_gt[2][1][0],measurements_gt[2][2][0]],'C2',linestyle='dashed')   #draw lines
        ax[0].plot([measurements_gt[3][1][1],measurements_gt[3][2][1]],[measurements_gt[3][1][0],measurements_gt[3][2][0]],'C2',linestyle='dashed')   #draw lines

        #ax[1].plot([measurements_fmm[2][1][1],measurements_fmm[2][2][1],measurements_fmm[3][1][1],measurements_fmm[3][2][1]],[measurements_fmm[2][1][0],measurements_fmm[2][2][0],measurements_fmm[3][1][0],measurements_fmm[3][2][0]],'ro')   #draw lines
        ax[1].plot([measurements_fmm[2][1][1],measurements_fmm[2][2][1]],[measurements_fmm[2][1][0],measurements_fmm[2][2][0]],'r',linestyle='dashed')   #draw lines
        ax[1].plot([measurements_fmm[3][1][1],measurements_fmm[3][2][1]],[measurements_fmm[3][1][0],measurements_fmm[3][2][0]],'r',linestyle='dashed')   #draw lines

        #ax[2].plot([measurements_ac[2][1][1],measurements_ac[2][2][1],measurements_ac[3][1][1],measurements_ac[3][2][1]],[measurements_ac[2][1][0],measurements_ac[2][2][0],measurements_ac[3][1][0],measurements_ac[3][2][0]],'bo')   #draw lines
        ax[2].plot([measurements_ac[2][1][1],measurements_ac[2][2][1]],[measurements_ac[2][1][0],measurements_ac[2][2][0]],'b',linestyle='dashed')   #draw lines
        ax[2].plot([measurements_ac[3][1][1],measurements_ac[3][2][1]],[measurements_ac[3][1][0],measurements_ac[3][2][0]],'b',linestyle='dashed')   #draw lines

        for axi in ax.flat:
            axi.xaxis.set_major_locator(plt.MultipleLocator(tick_rate))
            axi.yaxis.set_major_locator(plt.MultipleLocator(tick_rate))
            axi.yaxis.set_minor_locator(plt.MultipleLocator(2))
            axi.xaxis.set_minor_locator(plt.MultipleLocator(2))
            axi.xaxis.set_major_formatter(FuncFormatter(double_ticks))
            axi.yaxis.set_major_formatter(FuncFormatter(double_ticks))
        fig.tight_layout(pad=1.2)
        cavolo = ""
        if nod[2] < 10:
            cavolo = "0"
        #plt.savefig("Images/"+stringhetta+"/"+stringhetta+"-"+cavolo+str(nod[2]), bbox_inches='tight')
        plt.show()"""

    """number_of_nodules = len(nodules)
    for index in range(1,number_of_nodules+1):
        print(str(index)+"&"+str(iou_list_fmm[index-1])+"&"+str(major_axis_err_list_fmm[index-1])+"&"+str(minor_axis_err_list_fmm[index-1])+"&"+str(iou_list_ac[index-1])+"&"+str(major_axis_err_list_ac[index-1])+"&"+str(minor_axis_err_list_ac[index-1]))
    major_axis_err_fmm = np.array(major_axis_err_list_fmm)
    minor_axis_err_fmm = np.array(minor_axis_err_list_fmm)
    major_axis_err_ac = np.array(major_axis_err_list_ac)
    minor_axis_err_ac = np.array(minor_axis_err_list_ac)
    x = np.arange(1,len(major_axis_err_list_fmm)+1)
    fig, ax = plt.subplots(2,1)
    ax[0].plot(x,major_axis_err_fmm,'r')
    ax[0].plot(x,major_axis_err_ac,'b')
    ax[1].plot(x,minor_axis_err_fmm,'r')
    ax[1].plot(x,minor_axis_err_ac,'b')
    ax[0].set_xlim([1,number_of_nodules])
    ax[0].set_xticks(x)
    ax[0].grid()
    ax[0].yaxis.set_major_formatter(PercentFormatter())
    ax[1].yaxis.set_major_formatter(PercentFormatter())
    ax[1].set_xlim([1,number_of_nodules])
    ax[1].set_xticks(x)
    ax[1].grid()
    plt.show()"""


    """maj_ax_ell = np.array(major_axis_ellipse_list)   #Comparing ellipse and non
    min_ax_ell = np.array(minor_axis_ellipse_list)
    maj_ax = np.array(major_axis_list)
    min_ax = np.array(minor_axis_list)
    x = np.arange(1,len(minor_axis_list)+1)
    plt.grid()
    plt.plot(x,maj_ax_ell,'r')
    plt.plot(x,min_ax_ell,'b')
    plt.plot(x,maj_ax,'y')
    plt.plot(x,min_ax,'g')
    plt.show()"""
