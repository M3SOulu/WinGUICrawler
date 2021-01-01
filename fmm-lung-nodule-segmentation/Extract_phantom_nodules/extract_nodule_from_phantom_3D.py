"""
    This code can preprocess DICOM Lung images and extract nodules from phantom ( or any scan, by proving nodule location )
    Kyoto Institute of Technology [Visual Information]
    Marko Savic
"""
import json
import numpy as np # linear algebra
import pydicom
import os
import scipy.ndimage as ndi
import glob
from skimage.segmentation import clear_border
import matplotlib.pyplot as plt
import warnings
from skimage.measure import label,regionprops,marching_cubes_lewiner
from skimage.morphology import binary_dilation, binary_opening, disk, binary_erosion, binary_closing
from skimage.filters import roberts
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import imageio
import csv
from skimage.morphology import convex_hull_image

# Some constants
#INPUT_FOLDER = './Volume/S208960/'
INPUT_FOLDER = './Volume/S225190/'
patients = []

for root, dirs, files in os.walk(INPUT_FOLDER):
    path = root.split(os.sep)
    for file in files:
        if file[-3]+file[-2]+file[-1] == "dcm":
            patients.append((path[-1]))
            break

#Creates Frequency response of 2D Butterworth LPF with desired cutoff frequency and grade
def Butterworth_2D_LPF(size,cutoff,n):
    rows = size[0]
    cols = size[1]
    x = (np.ones((rows,1))*np.arange(1,cols+1) - (np.fix(cols/2) + 1))/cols
    y = (np.arange(1,rows+1)[:,np.newaxis] * np.ones((1,cols)) - (np.fix(rows/2) + 1))/rows
    radius = np.sqrt(np.square(x)+np.square(y))
    Filter = 1 / np.sqrt(1.0 + np.power(radius/cutoff,2*n))
    return Filter

def ImPlot2D3D(img, cmap=plt.cm.jet):

    Z = img[::1, ::1]

    """fig = plt.figure(figsize=(14, 7))
    fig.suptitle('2D Butterworth Filter', fontsize=16)
    # 2D Plot
    ax1 = fig.add_subplot(1, 2, 1)
    im = ax1.imshow(Z, cmap=cmap)
    ax1.set_title('2D')
    ax1.grid(False)"""

    # 3D Plot
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    X, Y = np.mgrid[:Z.shape[0], :Z.shape[1]]
    ax2.plot_surface(X, Y, Z, cmap=cmap)
    ax2.set_title('3D')

def Fourier_analysis(original,after_resample,cut_off,n):
    fig = plt.figure()
    cmap=plt.cm.viridis
    originalFFT = np.fft.fftshift(np.fft.fft2(original))
    originalFFTMagnSpec = 20*np.log(np.abs(originalFFT))
    Z = originalFFTMagnSpec[::1, ::1]
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    X, Y = np.mgrid[:Z.shape[0], :Z.shape[1]]
    im = ax1.plot_surface(X, Y, Z, cmap=cmap)
    clim=im.properties()['clim']
    ax1.set_title('1 - Original')
    ax1.set_zlim(50, 300)

    after_resampleFFT = np.fft.fftshift(np.fft.fft2(after_resample))
    after_resampleFFTMagnSpec = 20*np.log(np.abs(after_resampleFFT))
    Z = after_resampleFFTMagnSpec[::1, ::1]
    ax2 = fig.add_subplot(2, 2, 2, projection='3d')
    X, Y = np.mgrid[:Z.shape[0], :Z.shape[1]]
    ax2.plot_surface(X, Y, Z, cmap=cmap,clim=clim)
    ax2.set_title('2 - Resampled')
    ax2.set_zlim(50, 300)

    Filter_2D = Butterworth_2D_LPF(after_resampleFFT.shape,cut_off,n)
    Z = Filter_2D[::1, ::1]
    ax3 = fig.add_subplot(2, 2, 3, projection='3d')
    X, Y = np.mgrid[:Z.shape[0], :Z.shape[1]]
    ax3.plot_surface(X, Y, Z, cmap=cmap,clim=clim)
    ax3.set_title('3 - LPF')

    afterFilteringFFT = after_resampleFFT * Filter_2D
    afterFilteringFFTMagnSpec = 20*np.log(np.abs(afterFilteringFFT))
    Z = afterFilteringFFTMagnSpec[::1, ::1]
    ax4 = fig.add_subplot(2, 2, 4, projection='3d')
    X, Y = np.mgrid[:Z.shape[0], :Z.shape[1]]
    ax4.plot_surface(X, Y, Z, cmap=cmap,clim=clim)
    ax4.set_title('4 - Filtered')
    ax4.set_zlim(50, 300)
    plt.show()
    """fig,ax = plt.subplots(1,4)
    im = ax[0].imshow(originalFFTMagnSpec)
    clim=im.properties()['clim']
    ax[1].imshow(after_resampleFFTMagnSpec,clim=clim)
    ax[2].imshow(Filter_2D,clim=clim)
    ax[3].imshow(afterFilteringFFTMagnSpec,clim=clim)
    plt.show()"""
    exit()

#Apply LPF to every axial slice, with desired cutoff and grade(n=4 recommended)
def Apply_2D_LPF_Axial_Slice(image,cutoff,n):
    #fig,ax = plt.subplots(1,3)
    imageFFT = np.fft.fftshift(np.fft.fft2(image))  #Take slice to Frequency domain

    Filter_2D = Butterworth_2D_LPF(imageFFT.shape,cutoff,n)  #Calculate desired filter Frequency response
    imageFFT = imageFFT * Filter_2D                          #Apply filter
    imageIFFT = np.real(np.fft.ifft2(np.fft.ifftshift(imageFFT)))  #Take back to spatial domain
    #ax[2].imshow(20*np.log(np.abs(imageFFT.copy())))
    #ImPlot2D3D(Filter_2D)
    #ImPlot2D3D(20*np.log(np.abs(imageFFT.copy())))
    return imageIFFT

# Load the scans in given folder path
def load_scan(path):
    slices = [pydicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices

#Convert HU to pixel values
def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    image[image <=-2000] = 0

    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):

        # y = slope*x + intercept
        # The intercept is usually -1024, so air is approximately 0
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope

        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)

        image[slice_number] += np.int16(intercept)

    return np.array(image, dtype=np.int16)

#Correspond to real scale, if reresample set to True it can undo the rescaling
def resample(image, scan,new_spacing,reresample=False):
    # Determine current pixel spacing
    spacing = np.array(list(scan[0].PixelSpacing), dtype=np.float32)
    print(spacing)
    if reresample:
        spacing_temp = spacing
        spacing = new_spacing
        new_spacing = spacing_temp
    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor
    image = ndi.interpolation.zoom(image, real_resize_factor, mode='nearest')
    return image, new_spacing

def get_segmented_lungs_2D_slice(im,closing_size=10, plot=False):
    '''
    This funtion segments the lungs from the given 2D slice.
    '''
    if plot == True:
        fig,ax = plt.subplots(1,5)
        ax[0].imshow(im, cmap=plt.cm.bone)
        ax[0].axis('off')
        ax[0].set_title("Input")
    '''
    Step 1: Convert into a binary image.
    '''
    binary = np.array(im < -400, dtype=np.int8)
    if plot == True:
        ax[1].axis('off')
        ax[1].imshow(binary, cmap=plt.cm.bone)
        ax[1].set_title("Thresholded")
    '''
    Step 2: Remove the blobs connected to the border of the image.
    '''
    cleared = clear_border(binary)
    if plot == True:
        ax[2].axis('off')
        ax[2].imshow(cleared, cmap=plt.cm.bone)
        ax[2].set_title("Border blobs removed")
    '''
    Step 3: Label the image.
    '''
    label_image = label(cleared)
    """if plot == True:
        ax[0][3].axis('off')
        ax[0][3].imshow(label_image, cmap=plt.cm.bone)"""

    '''
    Step 4: Keep the labels with 2 largest areas.

    '''
    areas = [r.area for r in regionprops(label_image)]
    areas.sort()
    if len(areas) > 2:
        for region in regionprops(label_image):
            if region.area < areas[-2]:
                for coordinates in region.coords:
                       label_image[coordinates[0], coordinates[1]] = 0
    binary = label_image > 0
    """if plot == True:
        ax[1][0].axis('off')
        ax[1][0].imshow(binary, cmap=plt.cm.bone)"""

    '''
    Step 5: Erosion operation with a disk of radius 2. This operation is
    seperate the lung nodules attached to the blood vessels.

    '''
    selem = disk(2)
    binary = binary_erosion(binary, selem)
    """if plot == True:
        ax[1][1].axis('off')
        ax[1][1].imshow(binary, cmap=plt.cm.bone)"""

    '''
    Step 6: Closure operation with a disk of radius 10. This operation is
    to keep nodules attached to the lung wall.


    selem = disk(closing_size)
    binary = binary_closing(binary, selem)
    if plot == True:
        plots[5].axis('off')
        plots[5].imshow(binary, cmap=plt.cm.bone)
    '''
    """
    Step 7: Fill in the small holes inside the binary mask of lungs.
    """
    edges = roberts(binary)
    binary = ndi.binary_fill_holes(edges)
    if plot == True:
        ax[3].axis('off')
        ax[3].imshow(binary, cmap=plt.cm.bone)
        ax[3].set_title("Mask")
    '''
    Step 8: Superimpose the binary mask on the input image.
    '''
    get_high_vals = binary == 0
    im[get_high_vals] = 0
    if plot == True:
        ax[4].axis('off')
        ax[4].imshow(im, cmap=plt.cm.bone)
        ax[4].set_title("Result")
        plt.show()
    return im

MIN_BOUND = -1000.0
MAX_BOUND = 400.0


def normalize(image):
    image[image==0] = MIN_BOUND
    image = (image - MIN_BOUND) / (MAX_BOUND - MIN_BOUND)
    image[image>1] = 1.
    image[image<0] = 0.
    return image

def main():
    nodule_list_phantom = []
    nodule_list_phantom.append((163,233,157,5))
    nodule_list_phantom.append((124,283,157,10))
    nodule_list_phantom.append((182,308,167,20))
    nodule_list_phantom.append((381,228,155,5))
    nodule_list_phantom.append((405,269,153,10))
    nodule_list_phantom.append((347,319,155,20))
    nodule_list_phantom.append((159,221,199,20))
    nodule_list_phantom.append((120,256,206,5))
    nodule_list_phantom.append((120,309,206,10))
    nodule_list_phantom.append((175,307,212,20))
    nodule_list_phantom.append((384,222,200,5))
    nodule_list_phantom.append((412,265,203,5))
    nodule_list_phantom.append((363,271,201,10))
    nodule_list_phantom.append((396,315,204,10))
    nodule_list_phantom.append((342,326,204,20))

    """nodule_list_phantom.append((132,258,130,5))
    nodule_list_phantom.append((135,273,130,5))
    nodule_list_phantom.append((145,310,131,5))
    nodule_list_phantom.append((171,302,131,5))
    nodule_list_phantom.append((338,331,130,10))
    nodule_list_phantom.append((349,275,129,10))
    nodule_list_phantom.append((157,291,151,10))
    nodule_list_phantom.append((341,306,150,10))"""


    user_selected_spacing = [0.5,0.5]
    for patient in patients:
            current_patient = load_scan(INPUT_FOLDER+patient)
            for nodule in nodule_list_phantom:
                current_patient_pixels = get_pixels_hu(current_patient)
                current_patient_slice = current_patient_pixels[nodule[2]]
                warnings.filterwarnings("ignore") #ignore matplotlib warning
                if (current_patient[0].PixelSpacing[0]) < user_selected_spacing[1]:
                    current_patient_slice = Apply_2D_LPF_Axial_Slice(current_patient_slice,current_patient[0].PixelSpacing[0]/2,4)
                pix_resampled, spacing = resample(current_patient_slice, current_patient, user_selected_spacing)

                Fourier_analysis(current_patient_slice,pix_resampled,(user_selected_spacing[0]/current_patient[0].PixelSpacing[0])/2,4)

                if (current_patient[0].PixelSpacing[0]) >= user_selected_spacing[1]:
                    pix_resampled = Apply_2D_LPF_Axial_Slice(pix_resampled,(current_patient[0].PixelSpacing[0])/2,4)

                print("Shape before resampling\t", current_patient_slice.shape)
                print("Shape after resampling\t", pix_resampled.shape)
                segmented = pix_resampled.copy()
                segmented = get_segmented_lungs_2D_slice(segmented,plot=True)
                segmented = normalize(segmented)
                """fig ,ax = plt.ots(1,2)
                fig.suptitle(" Path: "+str(patient)+" | PixelSpacing: "+str(current_patient[0].PixelSpacing)+"\n | SliceThickness: "+str(current_patient[0].SliceThickness)+" | KVP: "+str(current_patient[0].KVP)+" | XRayTubeCurrent: "+str(current_patient[0].XRayTubeCurrent))
                ax[0].imshow(current_patient_slice)
                ax[1].imshow(segmented)
                plt.show()"""
                x=int((current_patient[0].PixelSpacing[0]/user_selected_spacing[0])*float(nodule[0]))
                y=int((current_patient[0].PixelSpacing[1]/user_selected_spacing[1])*float(nodule[1]))
                cube_size = int((1/user_selected_spacing[0])*nodule[3])
                cropped = segmented[y-cube_size:y+cube_size,x-cube_size:x+cube_size]
                if cropped[cube_size,cube_size] == 0:
                    crop_from_resampled = pix_resampled[y-cube_size:y+cube_size,x-cube_size:x+cube_size]
                    binary = cropped.copy()
                    binary[binary>0]=1
                    chull = convex_hull_image(binary)
                    cropped = crop_from_resampled*chull
                    cropped = normalize(cropped)
                print(cropped.shape)
                print(patient)
                """if cropped.shape[0]<=40:
                    cropped = ndi.interpolation.zoom(cropped, [2,2], mode='nearest')
                    cropped = Apply_2D_LPF_Axial_Slice(cropped,1/4,2)"""

                imageio.imwrite("saved_nodules/"+"nod="+str(nodule_list_phantom.index(nodule))+"_KVP="+str(current_patient[0].KVP)+"_XRayTubeCurrent="+str(current_patient[0].XRayTubeCurrent)+"_Path="+str(patient).replace("/","_")+"-"+str(nodule[3])+"mm.png",cropped)
                #np.save("saved_nodules/"+"nod="+str(nodule_list_phantom.index(nodule))+"_KVP="+str(current_patient[0].KVP)+"_XRayTubeCurrent="+str(current_patient[0].XRayTubeCurrent)+"_Path="+str(patient).replace("/","_")+"_diam="+str(nodule[3])+".npy",cropped)
                """fig ,ax = plt.ots(1,1)
                ax.imshow(cropped)
                print(nodule)
                ax.set_title(" Path: "+str(patient)+" | PixelSpacing: "+str(current_patient[0].PixelSpacing)+"\n | SliceThickness: "+str(current_patient[0].SliceThickness)+" | KVP: "+str(current_patient[0].KVP)+" | XRayTubeCurrent: "+str(current_patient[0].XRayTubeCurrent)+"\n"+"|y:"+str(nodule[1])+"|x:"+str(nodule[0])+"|diam:"+str(nodule[3]))
                plt.show()"""

if __name__ == "__main__":
    main()
