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
INPUT_FOLDER = './Slices/S10/'
patients = []

for root, dirs, files in os.walk(INPUT_FOLDER):
    path = root.split(os.sep)
    for file in files:
        if file[-3]+file[-2]+file[-1] == "dcm":
            patients.append((path[-1]+"/"+file))

#Creates Frequency response of 2D Butterworth LPF with desired cutoff frequency and grade
def Butterworth_2D_LPF(size,cutoff,n):
    rows = size[0]
    cols = size[1]
    x = (np.ones((rows,1))*np.arange(1,cols+1) - (np.fix(cols/2) + 1))/cols
    y = (np.arange(1,rows+1)[:,np.newaxis] * np.ones((1,cols)) - (np.fix(rows/2) + 1))/rows
    radius = np.sqrt(np.square(x)+np.square(y))
    Filter = 1 / (1.0 + np.power(radius/cutoff,2*n))
    return Filter

#Apply LPF to every axial slice, with desired cutoff and grade(n=4 recommended)
def Apply_2D_LPF_Axial_Slice(image,cutoff,n):
    imageFFT = np.fft.fftshift(np.fft.fft2(image))  #Take slice to Frequency domain
    Filter_2D = Butterworth_2D_LPF(imageFFT.shape,cutoff,n)  #Calculate desired filter Frequency response
    imageFFT = imageFFT * Filter_2D                          #Apply filter
    imageIFFT = np.real(np.fft.ifft2(np.fft.ifftshift(imageFFT)))  #Take back to spatial domain
    return imageIFFT

# Load the scans in given folder path
def load_scan(filename):
    slices = [pydicom.read_file(s) for s in glob.glob(filename)]
    slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
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
        f, plots = plt.subplots(8, 1, figsize=(5, 40))
    '''
    Step 1: Convert into a binary image.
    '''
    binary = np.array(im < -400, dtype=np.int8)
    if plot == True:
        plots[0].axis('off')
        plots[0].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 2: Remove the blobs connected to the border of the image.
    '''
    cleared = clear_border(binary)
    if plot == True:
        plots[1].axis('off')
        plots[1].imshow(cleared, cmap=plt.cm.bone)
    '''
    Step 3: Label the image.
    '''
    label_image = label(cleared)
    if plot == True:
        plots[2].axis('off')
        plots[2].imshow(label_image, cmap=plt.cm.bone)

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
    if plot == True:
        plots[3].axis('off')
        plots[3].imshow(binary, cmap=plt.cm.bone)

    '''
    Step 5: Erosion operation with a disk of radius 2. This operation is
    seperate the lung nodules attached to the blood vessels.

    '''
    selem = disk(2)
    binary = binary_erosion(binary, selem)
    if plot == True:
        plots[4].axis('off')
        plots[4].imshow(binary, cmap=plt.cm.bone)

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
        plots[6].axis('off')
        plots[6].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 8: Superimpose the binary mask on the input image.
    '''
    get_high_vals = binary == 0
    im[get_high_vals] = 0
    if plot == True:
        plots[7].axis('off')
        plots[7].imshow(im, cmap=plt.cm.bone)
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
    nodule_list_phantom.append((125,177,5))
    nodule_list_phantom.append((90,227,5))
    nodule_list_phantom.append((147,234,10))
    nodule_list_phantom.append((107,286,10))
    nodule_list_phantom.append((171,301,20))
    nodule_list_phantom.append((366,283,20))
    nodule_list_phantom.append((429,286,10))
    nodule_list_phantom.append((387,182,20))
    nodule_list_phantom.append((431,225,5))
    user_selected_spacing = [0.5,0.5]
    for patient in patients:
            first_patient = load_scan(INPUT_FOLDER+patient)
            first_patient_pixels = get_pixels_hu(first_patient)
            first_patient_slice = first_patient_pixels[0]
            warnings.filterwarnings("ignore") #ignore matplotlib warning
            if (first_patient[0].PixelSpacing[0]) < user_selected_spacing[1]:
                first_patient_slice = Apply_2D_LPF_Axial_Slice(first_patient_slice,first_patient[0].PixelSpacing[0]/2,2)
            pix_resampled, spacing = resample(first_patient_slice, first_patient, user_selected_spacing)
            if (first_patient[0].PixelSpacing[0]) >= user_selected_spacing[1]:
                pix_resampled = Apply_2D_LPF_Axial_Slice(pix_resampled,(1/first_patient[0].PixelSpacing[0])/2,2)
            print("Shape before resampling\t", first_patient_slice.shape)
            print("Shape after resampling\t", pix_resampled.shape)
            segmented = pix_resampled.copy()
            segmented = get_segmented_lungs_2D_slice(segmented)
            segmented = normalize(segmented)
            """fig ,ax = plt.subplots(1,2)
            fig.suptitle(" Path: "+str(patient)+" | PixelSpacing: "+str(first_patient[0].PixelSpacing)+"\n | SliceThickness: "+str(first_patient[0].SliceThickness)+" | KVP: "+str(first_patient[0].KVP)+" | XRayTubeCurrent: "+str(first_patient[0].XRayTubeCurrent))
            ax[0].imshow(first_patient_slice)
            ax[1].imshow(segmented)
            plt.show()"""
            for nodule in nodule_list_phantom:
                x=int((first_patient[0].PixelSpacing[0]/user_selected_spacing[0])*float(nodule[0]))
                y=int((first_patient[0].PixelSpacing[1]/user_selected_spacing[1])*float(nodule[1]))
                cube_size = int((1/user_selected_spacing[0])*nodule[2])
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
                imageio.imwrite("saved_nodules/"+"nod="+str(nodule_list_phantom.index(nodule))+"_KVP="+str(first_patient[0].KVP)+"_XRayTubeCurrent="+str(first_patient[0].XRayTubeCurrent)+"_Path="+str(patient).replace("/","_")+".jpg",cropped)
                np.save("saved_nodules/"+"nod="+str(nodule_list_phantom.index(nodule))+"_KVP="+str(first_patient[0].KVP)+"_XRayTubeCurrent="+str(first_patient[0].XRayTubeCurrent)+"_Path="+str(patient).replace("/","_")+".npy",cropped)
                """fig ,ax = plt.subplots(1,1)
                ax.imshow(cropped)
                print(nodule)
                ax.set_title(" Path: "+str(patient)+" | PixelSpacing: "+str(first_patient[0].PixelSpacing)+"\n | SliceThickness: "+str(first_patient[0].SliceThickness)+" | KVP: "+str(first_patient[0].KVP)+" | XRayTubeCurrent: "+str(first_patient[0].XRayTubeCurrent)+"\n"+"|y:"+str(nodule[1])+"|x:"+str(nodule[0])+"|diam:"+str(nodule[2]))
                plt.show()"""

if __name__ == "__main__":
    main()
