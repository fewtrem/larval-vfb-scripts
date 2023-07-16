'''
Created on 28 Aug 2016

@author: s1144899

The helper functions

'''
import numpy as np
from scipy import ndimage
import datetime,os,ctypes
dir_path = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.cdll.LoadLibrary(os.path.join(os.path.join(dir_path,'CFunc'),'uniqueVals.so'))
cUniqueVals = lib.uniqueVals

# Get a ROI for measuring scoring of this image by removing small voxel groups: 
def makeScoringRegionROI(settings,thisDataNTemp):
    print "Pipeline: Doing quick thresholding to calculate scoring region..."
    da = datetime.datetime.now()
    # Get the connected zones:
    struct=ndimage.generate_binary_structure(3,2)
    rep = ndimage.label(thisDataNTemp,struct,output=np.int32)
    # overwrite it:
    thisDataNTemp = np.zeros(thisDataNTemp.shape,dtype=np.uint8)
    # a low memory C function to get the sizes:
    theFreq = np.zeros(rep[1]+1,dtype=np.int32)
    theFreq = np.ascontiguousarray(theFreq)
    sizeLoop = np.product(np.array(rep[0].shape))
    cUniqueVals(ctypes.c_void_p(rep[0].ctypes.data),
             ctypes.c_long(long(sizeLoop)),
             ctypes.c_void_p(theFreq.ctypes.data))
    for i in range(1,len(theFreq)):
        # remove small specles:
        # Note we have combined the images, which is fine as smallest kept region will still be in the final image!
        if theFreq[i]>settings['vMaxSpecleSize']:
            if i!=0:
                thisDataNTemp[rep[0]==i]=1
    db = datetime.datetime.now()
    print "Pipeline: Done Thresholding, took ", (db-da), " seconds"
    return thisDataNTemp

# Get a rectangular ROI from storage array data:
# Note it gets the upper bound (that does not include a signal voxel, is one above)
def getRectROI(settings,thisDataN):
    mAdd = np.array(settings['mAdd'])+np.multiply(np.array(settings['exploreB'])+np.array(settings['convB']),np.array(settings['skipdips']))
    print "Pipeline: Getting the ROI..."
    print "Pipeline:   Adding the borders of ",mAdd
    sums = []
    #ROI calculator from signal channels:
    tSUMS = np.sum(thisDataN,axis=2)
    #x sums:
    sums.append(np.sum(tSUMS,axis=1)>0)
    #y sums:
    sums.append(np.sum(tSUMS,axis=0)>0)
    del tSUMS
    #z sums:
    #remember that summing axis 0 means axes shift:
    sums.append(np.sum(np.sum(thisDataN,axis=0),axis=0)>0)
    ROI = []
    #x,y,z
    for i in range(3):
        if np.sum(sums[i]) != 0:
            ROI.append([np.argmax(sums[i])-mAdd[i],len(sums[i])-np.argmax(sums[i][::-1])+mAdd[i]])
        else:
            ROI.append([0,0])
    # Sanity Check:
    thisShape = thisDataN.shape
    for Ri in range(3):
        for Rj in range(2):
            if ROI[Ri][Rj]>thisShape[Ri]:
                ROI[Ri][Rj] = thisShape[Ri]
            if ROI[Ri][Rj]<0:
                ROI[Ri][Rj] = 0
    return ROI

# A function to get the size of the ROI:
def getROIDiffs(ROIIn):
    return np.array((ROIIn[0][1]-ROIIn[0][0],ROIIn[1][1]-ROIIn[1][0],ROIIn[2][1]-ROIIn[2][0]))
# A function to copy the ROI:
def copyROI(ROIIn):
    return [[ROIIn[0][0],ROIIn[0][1]],[ROIIn[1][0],ROIIn[1][1]],[ROIIn[2][0],ROIIn[2][1]]]

# Split the ROIs up into ones that, with the border, are smaller than the maximum size:
def splitUpROI(settings,ROI):
    borderWidth = settings['totalBorderWidth']
    ROIListToCheck = [ROI]
    FinalROIList = []
    while len(ROIListToCheck)>0:
        thisROI = ROIListToCheck.pop()
        # Split the ROI along its longest axis into 2 if too big and add in a boundary:
        # we want to find the max dim of the ROI, so let's get the widths:
        roiDiffs = getROIDiffs(thisROI)
        # first we need to see if it is too big:
        roiDiffsB = roiDiffs+ np.array(borderWidth)*2
        prodDiffs = np.prod(roiDiffsB)
        if prodDiffs>settings['maxVoxels']:
            # split it
            maxI = np.argmax(roiDiffs)
            splitLim = roiDiffs[maxI]/2+thisROI[maxI][0] # will always round down when it can!
            newROIA = copyROI(thisROI)
            newROIA[maxI][1]=splitLim
            ROIListToCheck.append(newROIA)
            newROIB = copyROI(thisROI)
            newROIB[maxI][0]=splitLim
            ROIListToCheck.append(newROIB)
        else:
            FinalROIList.append(thisROI)
    return FinalROIList
# Add a border to the ROI and check it is in limits.
# Returns the new ROI and also the slicing params to populate the new subImg (see below):
'''
totalDims = getROIDiffs(thisROI) + np.array(borderWidth)*2
subImg = np.zeros(totalDims,dtype=np.uint8)
actualROI,adjustedWidths = addBorder(thisROI,borderWidth,origImg.shape,subImg.shape)
subImg[adjustedWidths[0][0]:adjustedWidths[0][1],adjustedWidths[1][0]:adjustedWidths[1][1],adjustedWidths[2][0]:adjustedWidths[2][1]]=\
origImg[actualROI[0][0]:actualROI[0][1],actualROI[1][0]:actualROI[1][1],actualROI[2][0]:actualROI[2][1]]
'''
# note subShape is basically bounds +2*borderIn
def addBorder(ROIIn,borderIn,bounds,subShape):
    # Update it to get desired ROI:
    tempROI = copyROI(ROIIn)
    for i in range(3):
        tempROI[i][0] -= borderIn[i]
        tempROI[i][1] += borderIn[i]
    # Now validate it:
    newROI = copyROI(tempROI)
    widthAdjustments = []
    for i in range(3):
        # Correct ROI if required:
        for j in range(2):
            if newROI[i][j]<0:
                newROI[i][j] = 0
            elif newROI[i][j]>bounds[i]:
                newROI[i][j] = bounds[i]
        # Calculate the difference to the desired one:
        widthAdjustmentsA = []
        # the difference of the starting index to the old one:
        widthAdjustmentsA.append(newROI[i][0]-tempROI[i][0])
        # the difference of the finishing index to the old one plus the desired difference:
        widthAdjustmentsA.append(newROI[i][1]-tempROI[i][1]+subShape[i])
        # (Also the above plus the width of the ROI:)
        #widthAdjustmentsA.append(newROI[i][1]-tempROI[i][0])
        widthAdjustments.append(widthAdjustmentsA)
    return newROI,widthAdjustments