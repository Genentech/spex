####################################################################################
#  SPEX SEGMENTATION MODULE - Functions for single-cell segmentation in FOV Images #
####################################################################################

import os
import numpy as np
import pandas as pd
import matplotlib as plt
import math
import json

from aicsimageio import AICSImage, imread_dask
from aicsimageio.vendor.omexml import OMEXML
from tifffile import TiffFile

from sklearn.neighbors import NearestNeighbors
from skimage.filters import median, gaussian,threshold_otsu
from skimage.filters import threshold_otsu
from skimage.exposure import rescale_intensity
from skimage.measure import label, regionprops_table, regionprops
from skimage.feature import peak_local_max
from skimage.morphology import watershed, dilation, opening, erosion, disk,binary_dilation
from skimage.segmentation import watershed, expand_labels
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.util import img_as_float, apply_parallel

import cv2

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

from stardist.models import StarDist2D, Config2D
from csbdeep.utils import normalize 
import mxnet
from cellpose import models
from deepcell.applications import Mesmer

####################################################################################
#                            I/O FUNCTIONS 
####################################################################################


def load_tiff(img,is_mibi=True):
    
    """Load image and check/correct for dimension ordering
    
    Parameters
    ----------
    image : Path of Multichannel tiff file
    is_mibi:Boolean. Does this image come from MIBI?
 
    Returns
    -------
    Image Stack : 2D numpy array
    Channels : list
    
    """
    file=img
    img = AICSImage(img)
    
    channel_len=max(img.size("STCZ")) #It is assumed that the dimension with largest length has the channels
    order=("S","T","C","Z")
    dim=img.shape

    x=0
    for x in range(5):
        if dim[x]==channel_len:
            break
    order[x]
    string=str(order[x])
    string+="YX"
    
    if string=="SYX":
        ImageDASK=img.get_image_dask_data(string,T=0,C=0,Z=0)
    if string=="TYX":
        ImageDASK=img.get_image_dask_data(string,S=0,C=0,Z=0)
    if string=="CYX":
        ImageDASK=img.get_image_dask_data(string,S=0,T=0,Z=0)
    if string=="ZYX":
        ImageDASK=img.get_image_dask_data(string,S=0,T=0,C=0)
    
    ImageTrue = ImageDASK.compute()
    
    if is_mibi==True:
        Channel_list = []
        with TiffFile(file) as tif:
            for page in tif.pages:
                # get tags as json
                description = json.loads(page.tags['ImageDescription'].value)
                Channel_list.append(description['channel.target'])
                # only load supplied channels
                #if channels is not None and description['channel.target'] not in channels:
                    #continue

                    # read channel data
                    #Channel_list.append((description['channel.mass'],description['channel.target']))
    else:
        Channel_list=img.get_channel_names()
    
    return ImageTrue, Channel_list


####################################################################################
#                            PREPROCESSING FUNCTIONS 
####################################################################################

def background_subtract(Img, ch, top,subtraction):
    
    """Subtract background signal from other channels
    
    Parameters
    ----------
    image : Multichannel numpy array (C,X,Y)
    ch: int, Index of background channel
    top : int, ignore pixels above this threshold
    subtraction: int, how many intensity units to subract from other channels
 
    Returns
    -------
    Image Stack : Background corrected Image Stack
    
    """
    Background_ch=Img[ch]
    rawMaskDataCap = Background_ch
    
    rawMaskDataCap[np.where(rawMaskDataCap > top)] = top
    guassianbg= rescale_intensity(gaussian(rawMaskDataCap,sigma=3))
    
    level = threshold_otsu(guassianbg)
    mask1=(guassianbg>=level)*subtraction
    
    def background_subtract_wrap(array, mask=mask1):
        correct=array[0]-mask
        correct[np.where(correct < 0)] = 0
        return correct[np.newaxis, ...]
    
    bgcorrect=apply_parallel(background_subtract_wrap,Img, chunks=(1, Img.shape[1],Img.shape[2]), dtype='float')
    
    return bgcorrect


def nlm_denoise(Img,patch,dist):
    
    """Non local means denoising
    
    Parameters
    ----------
    image : Multichannel numpy array (C,X,Y)
    patch: int, Patch size (5 is typical)
    dist: int, ignore pixels above this threshold (6 is typical)
 
    Returns
    -------
    Image Stack : Denoised image stack as numpy array (C,X,Y)
    
    """
    
    def nlm_denoise_wrap(array):
        correct=array[0]
        sigma_est = np.mean(estimate_sigma(correct, multichannel=False))
        correct = denoise_nl_means(correct, h=0.6 * sigma_est, sigma=sigma_est,fast_mode=True,patch_size=patch, patch_distance=dist, multichannel=False, preserve_range=True)
        return correct[np.newaxis, ...]
    
    denoise=apply_parallel(nlm_denoise_wrap,Img, chunks=(1, Img.shape[1],Img.shape[2]), dtype='float',compute=True)
    
    return  denoise


def median_denoise(Img,kernal,ch):
    
    """Non local means denoising
    
    Parameters
    ----------
    image : Multichannel numpy array (C,X,Y)
    kernal: int, 5-7 is a typical range
    ch: list of int, indexes of channels to be denoised
 
    Returns
    -------
    Image Stack : Denoised image stack as numpy array (C,X,Y)
    
    """
    
    filterchannels=ch
    
    def median_denoise_wrap(array):
        correct=array[0]
        correct = median(correct, disk(kernal))
        return correct[np.newaxis, ...]
    
    denoise=apply_parallel(median_denoise_wrap,Img, chunks=(1, Img.shape[1],Img.shape[2]), dtype='float',compute=True)
    
    for i in range(0,Img.shape[0],1):
        if (i in filterchannels):
            temp=denoise[i]
            temp= np.expand_dims(temp,0)
            if i==0:
                filtered=temp
            else:
                filtered=np.concatenate((temp,filtered),axis=0)
        else:
            temp=Img[i]
            temp= np.expand_dims(temp,0)
            if i==0:
                filtered=temp
            else:
                filtered=np.concatenate((temp,filtered),axis=0)
                
    fdenoise=np.flip(filtered,axis=0)
    
    return  fdenoise

####################################################################################
#                            CELL SEGMENTATION FUNCTIONS 
####################################################################################

def stardist_cellseg(img, seg_channels, scaling, threshold, min, max):
    
    """Segment image by stardist deeplearning method
    
    Parameters
    ----------
    image : Multichannel image as numpy array
    seg_channels: list of indices to use for nuclear segmentation
    scaling: Integer value scaling
    threshold: probability cutoff
    min: bottom percentile normalization
    max: top percentile normalization
 
    Returns
    -------
    labels : per cell segmentation as numpy array
    
    """
    
    temp2=np.zeros((img.shape[1],img.shape[2]))
    for i in seg_channels:
        temp=img[i]
        temp2=temp+temp2
    
    SegImage=temp2
    SegImage = cv2.resize(SegImage, (SegImage.shape[1]*scaling, 
                         SegImage.shape[0]*scaling),
                        interpolation=cv2.INTER_NEAREST)
    
    model = StarDist2D.from_pretrained('2D_versatile_fluo') # model for multiplex IF images
    
    image_norm = normalize(SegImage[::1,::1], min, max) 
    labels, details = model.predict_instances(image_norm, prob_thresh=threshold)
    
    labels = cv2.resize(labels, (labels.shape[1]//scaling, 
                         labels.shape[0]//scaling),
                        interpolation=cv2.INTER_NEAREST)
    
    return labels


def cellpose_cellseg(img, seg_channels,diamtr, scaling):
    
    """Segment image by cellpose deeplearning method
    
    Parameters
    ----------
    image : Multichannel image as numpy array
    seg_channels: list of indices to use for nuclear segmentation
    diamtr: typical size of nucleus
    scaling: Integer value scaling
 
    Returns
    -------
    labels_final : per cell segmentation as numpy array
    
    """
    temp2=np.zeros((img.shape[1],img.shape[2]))
    for i in seg_channels:
        temp=img[i]
        temp2=temp+temp2
    
    SegImage=temp2
    SegImage = cv2.resize(SegImage, (SegImage.shape[1]*scaling, 
                         SegImage.shape[0]*scaling),
                        interpolation=cv2.INTER_NEAREST)
    
    #model = models.Cellpose(device=mxnet.cpu(), torch=False,gpu=False, model_type="nuclei")
    model = models.Cellpose(gpu=False, model_type="nuclei")
    
    labels, _, _, _ = model.eval([SegImage[::1, ::1]], channels=[[0,0]], diameter=diamtr)
    
    labels2=np.float32(labels[0])
    
    labels_final = cv2.resize(labels2, (labels2.shape[1]//scaling,labels2.shape[0]//scaling), interpolation=cv2.INTER_NEAREST)
    
    labels_final=np.uint32(labels_final)
    
    return labels_final

def deepcell_segmentation(img, seg_channels, mpp):

    """Segment image by deepcell deeplearning method

    Parameters
    ----------
    image : Multichannel image as numpy array
    seg_channels: list of indices to use for nuclear segmentation
    mpp: float, micron per pixel

    Returns
    -------
    labels_final : per cell segmentation as numpy array

    """
    temp2=np.zeros((img.shape[1],img.shape[2]))
    for i in seg_channels:
        temp=img[i]
        temp2=temp+temp2

    x=temp2
    y = np.expand_dims(x, axis=0)
    pseudoIF=np.stack((y,y), axis=3)

    app = Mesmer()
    y_pred = app.predict(pseudoIF, image_mpp=mpp, compartment='nuclear')

    labels=np.squeeze(y_pred)

    return labels


def classicwatershed_cellseg(img, seg_channels):
    
    """Detect nuclei in image using classic watershed
    
    Parameters
    ----------
    image : Multichannel image as numpy array
    seg_channels: list of indices to use for nuclear segmentation
    
    -------
    Returns
    -------
    dilated_labels : per cell segmentation as numpy array
    """
    
    temp2=np.zeros((img.shape[1],img.shape[2]))
    for i in seg_channels:
        temp=img[i]
        temp2=temp+temp2

    SegImage=temp2/len(seg_channels)
    med = median(SegImage, disk(3))
    
    local_max = peak_local_max(med, min_distance=2,indices=False)
    
    otsu = skimage.filters.threshold_otsu(med)
    otsu_mask = med > otsu

    otsu_mask = skimage.morphology.binary_dilation(otsu_mask, np.ones((2,2)))
    masked_peaks = local_max*otsu_mask

    seed_label = label(masked_peaks)

    watershed_labels = watershed(image = -med, markers = seed_label, 
                                 mask = otsu_mask, watershed_line=True,compactness=20)

    selem = disk(1)
    dilated_labels = erosion(watershed_labels, selem)
    selem = disk(1)
    dilated_labels = dilation(dilated_labels, selem)
    
    return dilated_labels


def rescue_cells(img,seg_channels, labeling):
    """Rescue/Segment cells that deep learning approach may have missed
    
    Parameters
    ----------
    Image : raw image 2d numpy array
    seg_channels: list of indices to use for nuclear segmentation
    label: numpy array of segmentation labels
 
    Returns
    -------
    combinelabel : 2D numpy array with added cells
    
    """
    temp2=np.zeros((img.shape[1],img.shape[2]))
    for i in seg_channels:
        temp=img[i]
        temp2=temp+temp2

    SegImage=temp2/len(seg_channels)
    
    props = regionprops_table(labeling, intensity_image=SegImage, 
                              properties=['mean_intensity','area'])

    meanint_cell= np.mean(props['mean_intensity'])
    meansize_cell=np.mean(props['area'])

    radius= math.floor(math.sqrt(meansize_cell/3.14)*0.5)
    threshold= meanint_cell*0.5
    
    med = median(SegImage, disk(radius))
    local_max = peak_local_max(med, min_distance=math.floor(radius*1.2),indices=False)

    mask = med > threshold

    mask = binary_dilation(mask, np.ones((2,2)))
    masked_peaks = local_max*mask

    seed_label = label(masked_peaks)

    watershed_labels = watershed(image = -med, markers = seed_label, 
                                 mask = mask, watershed_line=True,compactness=20)

    selem = disk(1)
    dilated_labels = erosion(watershed_labels, selem)
    selem = disk(1)
    dilated_labels = dilation(dilated_labels, selem)

    labels2=labeling>0

    props = regionprops(dilated_labels, intensity_image=labels2)

    labels_store = np.arange(np.max(dilated_labels) + 1)

    for cell in props:
        if (
            cell.mean_intensity >= 0.03
        ):
            labels_store[cell.label] = 0

    finalMask = labels_store[dilated_labels]

    combinelabel=(labeling+finalMask)
    combinelabel=label(combinelabel)
    
    return combinelabel

####################################################################################
#                            POSTPROCESSSING FUNCTIONS 
####################################################################################

def remove_small_objects(segments, minsize):
    
    """Remove small segmented objects
    
    Parameters
    ----------
    segments: numpy array of segmentation labels
    minsize: minimum pixel size
 
    Returns
    -------
    out : 2D label numpy array 
    
    """
    
    out = np.copy(segments)
    component_sizes = np.bincount(segments.ravel())
    
    too_small = component_sizes < minsize
    too_small_mask = too_small[segments]
    out[too_small_mask] = 0
    
    return out

def remove_large_objects(segments, maxsize):
    
    """Remove large segmented objects
    
    Parameters
    ----------
    segments: numpy array of segmentation labels
    minsize: max pixel size
 
    Returns
    -------
    out : 2D label numpy array 
    
    """
    
    out = np.copy(segments)
    component_sizes = np.bincount(segments.ravel())
    
    too_large = component_sizes > maxsize
    too_large_mask = too_large[segments]
    out[too_large_mask] = 0
    
    return out

def simulate_cell(label, dist):
    
    """Dilate labels by fixed amount to simulate cells
    
    Parameters
    ----------
    label: numpy array of segmentation labels
    dist: number of pixels to dilate
 
    Returns
    -------
    out : 2D label numpy array with simulated cells
    
    """
    
    expanded = expand_labels(label, dist)
    
    return expanded

####################################################################################
#                            DATA EXPORT FUNCTIONS 
####################################################################################

def feature_extraction(img, labels,channellist):
    
    """Extract per cell expression for all channels
    
    Parameters
    ----------
    img : Multichannel image as numpy array
    labels: 2d segmentation label numpy array
    channellist: list containing channel names
 
    Returns
    -------
    perCellDataDF : Pandas dataframe with cell by expression data
    
    """
    
    #Image=img
    #img = AICSImage(Image)
    
    #Get list of channels in ome.tiff
    Channels=channellist
    numchannels=len(Channels)
    
    #Read Image
    #img = load_tiff(imagepath)
    
    #Get coords from labels and create a dataframe to populate mean intensitoes
    props = regionprops_table(labels, properties=['label','centroid'])
    perCellDataDF = pd.DataFrame(props)

    #Loop through each tiff channel and append mean intensity to dataframe
    for x in range(0,numchannels,1):
        
        Image=img[x,:,:]
        
        props = regionprops_table(labels, intensity_image=Image, properties=['mean_intensity'])
        datatemp = pd.DataFrame(props)
        datatemp.columns = [Channels[x]]
        perCellDataDF=pd.concat([perCellDataDF,datatemp], axis=1)
    
    #export and save a .csv file
    #perCellDataDF.to_csv(image+'perCellDataCSV.csv')
    #perCellDataCSV=perCellDataDF.to_csv
    
    return perCellDataDF


####################################################################################
#                                  Utilities 
####################################################################################