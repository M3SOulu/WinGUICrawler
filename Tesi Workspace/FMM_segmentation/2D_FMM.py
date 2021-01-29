#!/usr/bin/env python
from matplotlib.widgets import Slider, Button, RadioButtons # import the Slider widget
from math import sqrt
#from __future__ import print_function
import matplotlib.pyplot as plt
import SimpleITK as sitk
import sys
import os
import numpy as np
from heapq import heappush, heappop
import time
from scipy.ndimage import binary_dilation
from skimage.measure import regionprops, label
from scipy.ndimage.interpolation import zoom
from mpl_toolkits.mplot3d import Axes3D
from skimage import filters
from skimage.filters import roberts
from skimage.morphology import disk, binary_closing
from skimage.morphology import convex_hull_image
from sklearn.cluster import KMeans
import imageio
import scipy.misc
from skimage import feature

class Status:   #Creates status matrix: -1 far point, 0 neighbor, 1 known point
                #Has same size as speed function F
                #Uses near2know and far2near functions
    def __init__(self,seed_list,F):   #Initialize the status matrix with -1 everywhere except for seed point where it is 0
        self.status = np.full(F.shape, -1)
        self.new_neighbors = []

    def setknown(self,point):     #Sets neighboring point to known
        self.status[point[0],point[1]] = 1

    def setnear(self,point,seed_id):     #Sets points surrounding the latest known point to neighbors
        self.new_neighbors = []    #uses list to keep track of newly added neighbor points
        if point[0] > 0 and self.status[point[0]-1,point[1]]!=1:  #Prevent index out of bounds and disturbing known points
            self.status[point[0]-1,point[1]] = 0
            self.new_neighbors.append(((point[0]-1,point[1]),seed_id))
        if point[0] < self.status.shape[0] - 1 and self.status[point[0]+1,point[1]]!=1:
            self.status[point[0]+1,point[1]] = 0
            self.new_neighbors.append(((point[0]+1,point[1]),seed_id))
        if point[1] > 0 and self.status[point[0],point[1]-1] != 1:
            self.status[point[0],point[1]-1] = 0
            self.new_neighbors.append(((point[0],point[1]-1),seed_id))
        if point[1] < self.status.shape[1] - 1 and self.status[point[0],point[1]+1] != 1:
            self.status[point[0],point[1]+1] = 0
            self.new_neighbors.append(((point[0],point[1]+1),seed_id))

class Times:              #Creates time matrix, addtime and calculatetime functions
    def __init__(self,seed_list,F):
        self.times = np.full(F.shape, np.inf) #Set all time matrix elements to inf except for seed
        for seed in seed_list:
            self.times[seed[0],seed[1]] = 0

    def addtime(self,value,point):   #Add new time value
        self.times[point[0],point[1]]=value

                                    #Uses formula from paper to calculate arrival time
    def calculatetime(self,point,F):     #Index out of bounds if not stopped on time
        j = point[0]
        i = point[1]
        T = self.times
        if ( j > 0 and j < (self.times.shape[0] - 1) ):  # normal cases for i and j
            b = min(T[j-1,i],T[j+1,i])
        if ( i > 0 and i < (self.times.shape[1] - 1) ):
            a = min(T[j,i-1],T[j,i+1])
        if j == 0:           #Edge cases
            b = T[j+1,i]
        if j == (self.times.shape[0] - 1):
            b = T[j-1,i]
        if i == 0:           #Edge cases
            a = T[j,i+1]
        if i == (self.times.shape[1] - 1):
            a = T[j,i-1]
        if ((1/F[j,i]) > abs(a-b)):
            Tji = (a+b+sqrt(2*((1/F[j,i])**2)-(a-b)**2))/2
        else:
            Tji = ((1/F[j,i])+min(a,b))
            #fig, axs = plt.subplots(1, 1, constrained_layout=True)
            #fig.suptitle(' a: '+str(a)+" | b: "+str(b), fontsize=16)
            #axs.imshow(self.times)
            #plt.show()
        return Tji

class HeapAndRegion:      #Keeps track of neighbors heap and matrix ( see paper )
    def __init__(self,seed_list,size):
        self.heap = []
        self.region = np.ones(size)*-1
        for seed in seed_list:
            self.check(0,seed,seed_list.index(seed))

    def push(self,point,Tcalc,seed_id):
        heappush(self.heap,(Tcalc,point,seed_id))
        self.region[point] = seed_id

    def replace(self,point,Tcalc,index,seed_id):      #replace element from heap
        del self.heap[index]
        self.push(point,Tcalc,seed_id)
        #self.heap.sort()               #really slows down, actually useless

    def check(self,Tcalc,point,seed_id):    #Check if the neighbor already has calculated time
        flag = False
        index = 0
        for element in self.heap:
            if element[1] == point:
                flag = True
                index = self.heap.index(element)
                break
        if flag == False:
            self.push(point,Tcalc,seed_id)
        else:
            if Tcalc < self.heap[index][0]:
                self.replace(point,Tcalc,index,seed_id)

class Cluster:    #handles regions, actually clusters
    def add_neighbor_clusters(self,cluster_list):
        dilated_mask = binary_dilation(self.mask).astype(int)
        for r in cluster_list:
            if (np.sum(np.multiply(dilated_mask,r.mask)) > 0):
                self.neighboring_clusters_list.append(r)

    def mean_of_cluster(self,input,padding_mask):
        return np.sum(self.mask*padding_mask*input)/np.sum(self.mask*padding_mask)

    def merge_clusters(self,connected_list,input,meano,padding_mask):
        for rn in self.neighboring_clusters_list:
            if (rn not in connected_list):
                mean_diff = (self.mean_of_cluster(input,padding_mask)-rn.mean_of_cluster(input,padding_mask))
                #print("IN:"+str(self.id)+"->CAND:"+str(rn.id)+"||"+" mean_diff: "+str(round(mean_diff,2)))
                if abs(mean_diff)<=meano or mean_diff<0:
                    #print(" ******************************************************************************* ")
                    #print("-- connecting cluster : "+str(self.id)+"<-> with cluster : "+str(rn.id))
                    #print(" ******************************************************************************* ")
                    connected_list.append(rn)
                    rn.merge_clusters(connected_list,input,meano,padding_mask)
        return connected_list

    def __init__(self,id,centroid,mask):
        self.centroid = centroid
        self.id = id
        self.neighboring_clusters_list = []
        self.mask = mask

def FMM(seed_list,F):
    stat = Status(seed_list,F)
    timez = Times(seed_list,F)
    heapregion = HeapAndRegion(seed_list,F.shape)

    iteration_counter = 0
    """plt.imshow(heapregion.region,cmap="tab20")
    plt.clim(0, 12)
    plt.axis("off")
    plt.show()"""
    while True:
        for nn in stat.new_neighbors:
            tcalc = timez.calculatetime(nn[0],F)
            heapregion.check(tcalc,nn[0],nn[1])
        smallest_value = heapregion.heap[0]
        heappop(heapregion.heap)
        iteration_counter += 1
        timez.addtime(smallest_value[0],smallest_value[1])
        stat.setknown(smallest_value[1])
        stat.setnear(smallest_value[1],smallest_value[2])
        """if iteration_counter == 500 or iteration_counter == 1000:
            plt.imshow(heapregion.region,cmap="tab20")
            plt.clim(0, 12)
            plt.axis("off")
            plt.show()"""

        if (len(heapregion.heap) == 0 ):
            break
    """plt.imshow(heapregion.region,cmap="tab20")
    plt.axis("off")
    plt.clim(0, 12)
    plt.show()"""
    return timez.times , heapregion.region

def grid(region_size,input_image,padding_mask,gradient):
    alpha = 1
    beta = 2
    grid_as_list = []
    input_shape = input_image.shape
    grad_mean_total = np.mean(gradient)
    half = int(region_size/2)
    for j in range(half,input_shape[0]-1,region_size):
        for i in range(half,input_shape[1]-1,region_size):
            if ( np.mean(gradient[j-half:j+half,i-half:i+half]) < alpha * grad_mean_total) and padding_mask[j,i]>0:
                grid_as_list.append((j,i))
            elif ( np.mean(gradient[j-half:j+half,i-half:i+half]) < beta * grad_mean_total):
                y0 = j
                x0 = i
                grad_list = []
                for jj in range(-half,half+1):
                    for ii in range(-half,half+1):
                        point = (jj+y0,ii+x0)
                        if (point[0] >= half and point[0] <= input_shape[0]-1-half and point[1] >= half and point[1] <= input_shape[1]-1-half ):
                            grad_list.append(((np.mean(gradient[point[0]-half:point[0]+half+1,point[1]-half:point[1]+half+1]),point)))
                pointo = grad_list[grad_list.index(min(grad_list))][1]
                if padding_mask[j,i]>0:
                    grid_as_list.append(pointo)
    griddo = np.zeros(shape)
    for point in grid_as_list:
            griddo[point[0],point[1]]=1
    return grid_as_list, griddo


def pad(input):  #Adds mean of all non zero neighboring values to missing pixels (0)
    for j in (range(input.shape[0])):
        for i in (range(input.shape[1])):
            if input[j,i] == 0:
                sum = 0
                count = 0
                if (j>0):
                    if input[j-1,i] > 0:
                        sum = sum + input[j-1,i]
                        count += 1
                if (j<input.shape[0]-1 ):
                    if input[j+1,i] > 0:
                        sum = sum + input[j+1,i]
                        count += 1
                if (i>0 ):
                    if input[j,i-1] > 0:
                        sum = sum + input[j,i-1]
                        count += 1
                if (i<input.shape[1]-1 ):
                    if input[j,i+1] > 0:
                        sum = sum + input[j,i+1]
                        count += 1
                if count!=0:
                    input[j,i] = (sum/count)
                else:
                    input[j,i] = 0
    return input

start = time.perf_counter()
INPUT_FOLDER = sys.argv[1]

mt0 = 0.15 #default slider values
cs0 = 7

count = 0
nodules = []
#walks the input directory and finds input images and their paths
for root, dirs, files in os.walk(INPUT_FOLDER):
    path = root.split(os.sep)
    for file in files:
        if file[-1] == "g" and file[-2]=="n" and file[-3]=="p" and file[-5] != "T" and file[-6] != "G":
            stringa = ""
            for p in path:
                stringa+=p+"/"
            nodules.append((file,stringa))

#reads and normalizes input image
for nod in nodules:
    print("------------------------------------------")
    print(nod)
    print("------------------------------------------")
    inputFilename = nod[1]+nod[0]
    sigma = float(1)
    input_image = imageio.imread(inputFilename)
    if(len(input_image.shape)) > 2:
        input_image=input_image[:,:,:-1]              #These 3 lines are in case the image is a 4 channel png
        input_image = np.asarray(input_image)
        input_image = np.dot(input_image, [0.299, 0.587, 0.114])

    input_image= (input_image - np.min(input_image))/(np.max(input_image)-np.min(input_image))
    rescale_factor = 0.5

    #if input_image.shape[0]>60:
    #    continue
    """    if input_image.shape[0]<=40:
        input_image = zoom(input_image, [2,2], mode='nearest')
        input_image = Apply_2D_LPF_Axial_Slice(input_image,1/4,2)
        rescale_factor = 0.25"""
    input_image[input_image < 0.02]=0
    input_image_copy=input_image.copy()
    padding_mask = input_image.copy()
    padding_mask[padding_mask>0] = 1
    #input_image = pad(input_image)

    inputImage = sitk.GetImageFromArray(input_image)
    inputImage = sitk.Cast(inputImage, sitk.sitkFloat32)
    smoothing = sitk.CurvatureAnisotropicDiffusionImageFilter()
    smoothing.SetTimeStep(0.125/2)
    smoothing.SetNumberOfIterations(5)
    smoothing.SetConductanceParameter(9.0)
    smoothingOutput = smoothing.Execute(inputImage)

    smooth = sitk.GetArrayFromImage(smoothingOutput)*padding_mask
    shape = smooth.shape
    print(shape)
    gradientMagnitude = sitk.GradientMagnitudeRecursiveGaussianImageFilter()
    gradientMagnitude.SetSigma(sigma)
    gradientMagnitudeOutput = gradientMagnitude.Execute(smoothingOutput)

    grad = sitk.GetArrayFromImage(gradientMagnitudeOutput)
    grad = (grad - np.min(grad))/(np.max(grad)-np.min(grad))

    tau = 2

    speed = np.exp(-tau*np.abs(grad))
    #FMM implementation starts

    """fig,ax = plt.subplots(1,2)
    ax[0].set_title("Padded Input")
    ax[1].set_title("Fixed Gradient")
    ax[0].axis('off')
    ax[1].axis('off')
    ax[0].imshow(smooth,cmap="bone")
    ax[1].imshow(grad)
    plt.show()
    continue"""
    grid_as_list, griddo = grid(3,smooth,padding_mask,grad)

    T,R = FMM(grid_as_list,speed)

    T = T * padding_mask
    T = (T - np.min(T))/(np.max(T)-np.min(T))
    print(" --- FMM execution time  : "+ str(time.perf_counter()-start))
    print(" ############################################################################### ")

    fig, ax = plt.subplots(1,1)
    plt.subplots_adjust(left=0.25, bottom=0.25)
    ax.imshow(input_image,cmap="gray")
    #plt.savefig("result_only_image/"+nod+"_cl_"+str(cluster_density)+"_mn_"+str(meano)+'.png')



    delta_cs = 1
    axcolor = 'lightgoldenrodyellow'
    axcs = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
    axmt = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
    scs = Slider(axcs, 'cluster density' ,3, 10, valinit=cs0, valstep=delta_cs)
    smt = Slider(axmt, 'mean threshold', 0, 0.3, valinit=mt0)

    def update(val):
        cluster_density = int(scs.val)
        meano = round(smt.val,2)
        start=time.perf_counter()
        grid_as_array = np.asarray(grid_as_list)
        cluster_grid, griddo_cluster = grid(cluster_density,smooth,padding_mask,grad)
        X = grid_as_array
        kmeans = KMeans(n_clusters=len(cluster_grid),init=np.asarray(cluster_grid),n_init=1)
        kmeans.fit(X)
        y_kmeans = kmeans.predict(X)
        #plt.scatter(X[:, 1], X[:, 0], c=y_kmeans, s=50, cmap='viridis')
        k_means_list = []
        centroids = np.round(kmeans.cluster_centers_,2)
        centroids_list = centroids.tolist()
        #plt.scatter(centroids[:, 1], centroids[:, 0], c='black', s=100, alpha=0.5);

        for q in range(y_kmeans.shape[0]):
            k_means_list.append((X[q][0],X[q][1],y_kmeans[q]))
        cluster_list = []
        for centroid in centroids_list:
            cluster_list.append(Cluster(centroids_list.index(centroid),centroid,np.zeros(shape)))
        for k in k_means_list:
            mini_region_mask = R.copy()
            mini_region_number = R[k[0],k[1]]
            mini_region_mask = (mini_region_mask == mini_region_number).astype(int)
            cluster_list[k[2]].mask += mini_region_mask
        Region_masku = np.zeros(shape).astype(int)
        for r in cluster_list:
            Region_masku = Region_masku+r.id*r.mask
            r.add_neighbor_clusters(cluster_list)

        Region_masku = Region_masku.astype(int)
        """fig,ax = plt.subplots(1,2)
        ax[0].imshow(input_image_copy)
        ax[1].imshow(roberts(Region_masku))
        plt.show()"""

        connected_list = []
        center_pixel = np.array([int(shape[0]/2),int(shape[1]/2)])
        """centroid_id = Region_masku[center_pixel]
        r_centroid = cluster_list[centroid_id]"""
        maximum_mean = 0
        max_reg = None
        for r in cluster_list:
            temp_max = r.mean_of_cluster(input_image,padding_mask)/np.linalg.norm(r.centroid-center_pixel)
            if temp_max > maximum_mean:
                maximum_mean = temp_max
                max_reg = r
        r_first = max_reg
        connected_list.append(r_first)
        connected_list = r_first.merge_clusters(connected_list,input_image_copy,meano,padding_mask)
        Mask = np.zeros(shape)
        for r in cluster_list:
            if r in connected_list:
                Mask = Mask + r.mask
        Mask = Mask * padding_mask
        print(" --- Total execution time  : "+ str(time.perf_counter()-start))
        #imageio.imwrite("result_only_mask/"+nod+"_cl_"+str(cluster_density)+"_mn_"+str(meano)+'.png', Mask)
        Borderu = binary_dilation(Mask)-Mask
        Borderu = (255*Borderu).astype(np.uint8)

        rgb_img = np.stack((input_image_copy,)*3, axis=-1)
        rgb_img = (255*rgb_img).astype(np.uint8)

        rgb_img[:,:,0][np.where(Borderu > 0)] = 255
        rgb_img[:,:,1][np.where(Borderu > 0)] = 0
        rgb_img[:,:,2][np.where(Borderu > 0)] = 0

        rgbTgriddo = np.stack((griddo,)*3, axis=-1)
        rgbTgriddo[:,:,1] = 0
        rgbTgriddo[:,:,2] = 0
        ax.imshow(rgb_img)
        ax.axis("off")
        #imageio.imwrite("results/"+inputFilename+'_segmented.png', Mask)
        #imageio.imwrite("results/"+inputFilename+'_border.png', rgb_img)

    update(scs)
    scs.on_changed(update)
    smt.on_changed(update)

    def next(event):
        plt.close()

    nextax = plt.axes([0.8, 0.025, 0.1, 0.04])
    button = Button(nextax, 'Next', color=axcolor, hovercolor='0.975')



    button.on_clicked(next)

    plt.show()


    """fig ,ax = plt.subplots(1,2)
    #ax[0].set_title("Input")
    ax[0].imshow(input_image_copy)
    #ax[1].plot([mp[1],mp2[1]], [mp[0],mp2[0]], '--', linewidth=2, color='red')
    #ax[1].set_title("Segmented nodule")
    ax[1].imshow(rgb_img)
    #plt.savefig("resultscomp/"+nod+"_cl_"+str(cluster_density)+"_mn_"+str(meano)+'.png')
    plt.show()"""


    """mean_region_map = np.zeros(shape)
    for r in cluster_list:
        mean_region_map += r.mean_of_cluster(input_image_copy.astype(int),padding_mask)+r.mask"""
    """fig ,ax = plt.subplots(4,2)
    im = ax[0][0].imshow(input_image_copy)
    ax[0][0].set_ylabel("Input")
    clim=im.properties()['clim']
    ax[0][1].imshow(T)
    ax[0][1].set_ylabel("Times")
    ax[1][0].imshow(griddo)
    ax[1][0].set_ylabel("Seed Grid")
    ax[1][1].imshow(mean_region_map)
    ax[1][1].set_ylabel("Times")
    ax[2][0].imshow(Region_masku*Mask,cmap="gray")
    ax[2][0].set_ylabel("T*Mask")
    ax[2][1].imshow(Region_masku*(1-Mask),cmap="gray")
    ax[2][1].set_ylabel("T*(1-Mask)")
    ax[3][0].imshow(Mask*input_image_copy, clim=clim)
    ax[3][0].set_ylabel("Mask*Input")
    ax[3][1].imshow((1-Mask)*input_image_copy, clim=clim)
    ax[3][1].set_ylabel("(1-Mask)*Input")
    #plt.savefig("results/"+nod+"_cl_"+str(cluster_density)+"_mn_"+str(meano)+'.png')
    plt.show()"""
