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
from skimage.morphology import binary_dilation, binary_opening, disk, binary_erosion, binary_closing,convex_hull_image
from skimage.filters import roberts
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import imageio
import csv


# Some constants
INPUT_FOLDER = './data/LIDC-IDRI/'
patients = []

for root, dirs, files in os.walk("."):
    path = root.split(os.sep)
    for file in files:
        if file == "000090.dcm":
            patients.append((path[-3]+"/"+path[-2]+"/"+path[-1],path[-3]))
print("fine intro")

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
def load_scan(path):
    slices = [pydicom.read_file(s) for s in glob.glob(path+'/*.dcm')]
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

def get_segmented_lungs_2D_slice(im,closing_size=20, plot=False):
    '''
    This funtion segments the lungs from the given 2D slice.
    '''
    im_blabla = im.copy()
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
    to keep nodules attached to the lung wall. (removed, solved by applying covex hull on cropped image)
    '''

    selem = disk(closing_size)
    binary_blabla = binary_closing(binary, selem)
    """if plot == True:
        plots[5].axis('off')
        plots[5].imshow(binary, cmap=plt.cm.bone)"""

    '''
    Step 7: Fill in the small holes inside the binary mask of lungs.
    '''
    edges = roberts(binary)
    binary = ndi.binary_fill_holes(edges)
    edges_blabla = roberts(binary_blabla)
    binary_blabla = ndi.binary_fill_holes(edges_blabla)
    if plot == True:
        plots[6].axis('off')
        plots[6].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 8: Superimpose the binary mask on the input image.
    '''

    get_high_vals = binary == 0
    im[get_high_vals] = 0
    get_high_vals_blabla = binary_blabla == 0
    im_blabla[get_high_vals_blabla] = 0

    if plot == True:
        plots[7].axis('off')
        plots[7].imshow(im, cmap=plt.cm.bone)
    return im, im_blabla

MIN_BOUND = -1000.0
MAX_BOUND = 400.0

def normalize(image):
    image[image==0] = MIN_BOUND
    image = (image - MIN_BOUND) / (MAX_BOUND - MIN_BOUND)
    image[image>1] = 1.
    image[image<0] = 0.
    return image

def main():
    print("inizio main")
    nodule_list_LIDC = []
    with open('annotations.csv', 'r') as f:
        reader = csv.reader(f)
        annotations_list = list(reader)
    with open('LIDC-IDRI_MetaData.csv', 'r') as f:
        reader = csv.reader(f)
        meta_list = list(reader)
    for ann in annotations_list:
        for meta in meta_list:
            if meta[9] == ann[0]:
                nodule_list_LIDC.append((meta[1],ann[1],ann[2],ann[3],ann[4]))
                break
    nodule_list_LIDC.sort()
    with open('nodule_list.txt', 'w') as f:
        f.write("{}\n".format("('LIDC_case', 'coordX', 'coordY', 'coordZ', 'diameter_mm')"))
        for item in nodule_list_LIDC:
            f.write("{}\n".format(item))
    print("inizio ciclo")
    user_selected_spacing = [0.5,0.5]
    patient_index=0
    nodule_index=0
    while True:
        if nodule_index>1185:
            break
        nodule = nodule_list_LIDC[nodule_index]
        print(nodule[0],"----",patients[patient_index][1])
        if nodule[0] == patients[patient_index][1]:
            print("nodule index: ",nodule_index," patient index: ",patient_index)
            first_patient = load_scan(INPUT_FOLDER + patients[patient_index][0])
            print(nodule," -------- is in -------- ",patients[patient_index][0])
            zz=round(abs(float(nodule[3])-first_patient[0].ImagePositionPatient[2])/first_patient[0].SliceThickness)
            first_patient_pixels = get_pixels_hu(first_patient)
            first_patient_slice = first_patient_pixels[zz]
            warnings.filterwarnings("ignore") #ignore matplotlib warning
            if (first_patient[0].PixelSpacing[0]) < user_selected_spacing[1]:
                first_patient_slice = Apply_2D_LPF_Axial_Slice(first_patient_slice,first_patient[0].PixelSpacing[0]/2,2)
            pix_resampled, spacing = resample(first_patient_slice, first_patient, user_selected_spacing)
            if (first_patient[0].PixelSpacing[0]) >= user_selected_spacing[1]:
                pix_resampled = Apply_2D_LPF_Axial_Slice(pix_resampled,(1/first_patient[0].PixelSpacing[0])/2,2)
            print("Shape before resampling\t", first_patient_slice.shape)
            print("Shape after resampling\t", pix_resampled.shape)
            segmented = pix_resampled.copy()
            segmented, binary_blabla = get_segmented_lungs_2D_slice(segmented)
            segmented = normalize(segmented)
            segmented_blabla = segmented.copy()
            s = first_patient
            x=int((1/user_selected_spacing[0])*round(abs(float(nodule[1])-s[0].ImagePositionPatient[0])))
            y=int((1/user_selected_spacing[1])*round(abs(float(nodule[2])-s[0].ImagePositionPatient[1])))
            cube_size = int(float(nodule[4])*(1/user_selected_spacing[1]))
            cropped = segmented[y-cube_size:y+cube_size,x-cube_size:x+cube_size]
            if cropped[cube_size,cube_size] == 0:
                crop_from_resampled = pix_resampled[y-cube_size:y+cube_size,x-cube_size:x+cube_size]
                binary = cropped.copy()
                binary[binary>0]=1
                chull = convex_hull_image(binary)
                cropped = crop_from_resampled*chull
                cropped = normalize(cropped)
            print(cropped.shape)
            """
            if cropped.shape[0]<=40:
                cropped = ndi.interpolation.zoom(cropped, [2,2], mode='nearest')
                cropped = Apply_2D_LPF_Axial_Slice(cropped,1/4,2)"""

            #imageio.imwrite("saved_nodules/"+nodule[0]+"-"+str(round(float(nodule[4]),2))+"mm"+"_un"+".jpg",cropped)
            #np.save("saved_nodules/"+nodule[0]+"-"+str(round(float(nodule[4]),2))+"mm"+".npy", cropped)
            """fig ,ax = plt.subplots(1,1)
            ax.imshow(cropped)
            ax.set_title("z:"+nodule[3]+"|y:"+nodule[2]+"|x:"+nodule[1]+"|diam:"+nodule[4])
            plt.show()"""

            fig ,ax = plt.subplots(1,4)
            ax[0].imshow(pix_resampled[y-cube_size:y+cube_size,x-cube_size:x+cube_size], cmap=plt.cm.bone)
            ax[0].set_title("Input")
            ax[0].axis("off")
            ax[1].imshow(segmented_blabla[y-cube_size:y+cube_size,x-cube_size:x+cube_size], cmap=plt.cm.bone)
            ax[1].set_title("Segmentation Error")
            ax[1].axis("off")
            ax[2].imshow(binary_blabla[y-cube_size:y+cube_size,x-cube_size:x+cube_size], cmap=plt.cm.bone)
            ax[2].set_title("Closing Fix")
            ax[2].axis("off")
            ax[3].imshow(cropped, cmap=plt.cm.bone)
            ax[3].set_title("Convex Hull Fix")
            ax[3].axis("off")
            plt.show()

            nodule_index+=1
        else:
            patient_index+=1

if __name__ == "__main__":
    main()

