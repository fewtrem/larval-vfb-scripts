'''
Created on 28 Jul 2016

@author: s1144899
'''


import numpy as np,nrrd2,datetime
from getWarp import getWarpField
from getWarp import smoothIntoLargeField
from getWarp import sparseSmoother
from getROIs import getRectROI
from getROIs import splitUpROI
from getROIs import getROIDiffs
from getROIs import addBorder
#from scipy import ndimage

# a function to get a single warp field: 
def getField(settings,preTempraw,nGraw,ROIImage):
    startGetFieldTime = datetime.datetime.now()
    print "Pipeline: Getting field..."
    # Update ROI from the prescribed image:
    if settings['getSpecificROI']==True:
        ROI = getRectROI(settings,ROIImage)
        settings['scoringROIUsed'] = ROI
    else:
        ROI = [[0,preTempraw.shape[0]],[0,preTempraw.shape[1]],[0,preTempraw.shape[2]]]
        settings['scoringROIUsed'] = ROI
    print "Pipeline: Scoring ROI: ",settings['scoringROIUsed']
    # calculate the border width from the other settings!
    convB = np.array(settings['convB'])
    skipdips = np.array(settings['skipdips'])
    exploreB = np.array(settings['exploreB'])
    tBW = (exploreB+convB)*skipdips+np.array(settings['prodForWarping'])
    settings['totalBorderWidth'] = tBW
    # store the output ROIs done individually:
    roisToDo = splitUpROI(settings,ROI)
    settings['subRoisUsed'] = roisToDo
    # we will want to store the field somewhere, and that's going to be a BIG file - ~1GB!
    fieldOut = np.zeros(list(preTempraw.shape)+[3],dtype=np.int8)
    print "Pipeline: Number of sub-ROIs: ",len(roisToDo)
    roiCount = 0
    for thisROI in roisToDo:
        roiCount+=1
        print "Pipeline:   Sub ROI: ",thisROI, "(",roiCount,"/",len(roisToDo),")"
        # get the dims with the border:
        totalDims = getROIDiffs(thisROI) + tBW*2
        # now create the subregions for the field calculator:
        preTempSl = np.zeros(totalDims,dtype=np.uint8)
        nGrawSl =  np.zeros(totalDims,dtype=np.uint8)
        # get the slice params:
        actualROI,adjustedWidths = addBorder(thisROI,tBW,preTempraw.shape,preTempSl.shape)
        # populate the subregions:
        preTempSl[adjustedWidths[0][0]:adjustedWidths[0][1],adjustedWidths[1][0]:adjustedWidths[1][1],adjustedWidths[2][0]:adjustedWidths[2][1]]=\
        preTempraw[actualROI[0][0]:actualROI[0][1],actualROI[1][0]:actualROI[1][1],actualROI[2][0]:actualROI[2][1]]
        nGrawSl[adjustedWidths[0][0]:adjustedWidths[0][1],adjustedWidths[1][0]:adjustedWidths[1][1],adjustedWidths[2][0]:adjustedWidths[2][1]]=\
        nGraw[actualROI[0][0]:actualROI[0][1],actualROI[1][0]:actualROI[1][1],actualROI[2][0]:actualROI[2][1]]
        # get the field low res (remember that inner convB and exploreB are zero:
        returnFieldLowRes = getWarpField(preTempSl,nGrawSl,settings)
        # the final output field smoothed out:
        returnFieldHiRes = smoothIntoLargeField(settings,returnFieldLowRes,preTempSl)
        # feed resultant field back to the full field:
        rS = returnFieldHiRes.shape
        fieldOut[thisROI[0][0]:thisROI[0][1],thisROI[1][0]:thisROI[1][1],thisROI[2][0]:thisROI[2][1],:]=returnFieldHiRes[tBW[0]:rS[0]-tBW[0],tBW[1]:rS[1]-tBW[1],tBW[2]:rS[2]-tBW[2],:]
        endGetFieldTime = datetime.datetime.now()
        print "Pipeline: Got Field, runtime:",(endGetFieldTime-startGetFieldTime)," seconds"
    return fieldOut


'''

Supplementary Functions!:

'''


# Get a score for stuff in the region of interest to help determine if we need to do more shifting....
def getROIScore(settings,ROIImageSl,returnFieldLowRes):
    singleScoreImg = getSingleScore(settings,returnFieldLowRes)
    ROISelector = ROIImageSl>0
    return [np.mean(singleScoreImg[ROISelector]),np.sum(ROISelector)]

# get the score as a single number:
def getSingleScore(settings,outPutW):
    scaler = np.power(np.array(settings['vScalerXYZ']),2)
    # go by dir to reduce size:
    sqOutput = np.zeros(outPutW.shape[0:3],dtype=np.float16)
    for i in range(3):
        thisOP = outPutW[:,:,:,i]
        sqOutput += np.multiply(thisOP.astype(np.float16),thisOP.astype(np.int))*scaler[i]
    sqOutput = np.sqrt(sqOutput)
    sqOutput[sqOutput>255]=255
    return sqOutput.astype(np.uint8)
# Take in bounds of the form orig:
#[[x1,x2],[y1,y2],[z1,z2]]
def getInBounds(orig,shapeLimits):
    corrected = [] 
    shifts = []
    for i in range(3):
        dimLims = orig[i]
        for j in range(2):
            correctedN = []
            shiftsN = []
            if dimLims[j]<0:
                correctedN = 0
                shiftsN = -dimLims[j]
            elif dimLims[j]>shapeLimits[i]:
                correctedN = shapeLimits[i]
                shiftsN = shapeLimits[i]-dimLims[j]
            else:
                correctedN = dimLims[j]
                shiftsN = 0
            corrected.append(correctedN)
            shifts.append(shiftsN)
    return corrected,shifts
# trying to avoid copying the field:
def exportFieldNRRD(settings,storage,field):
    # get a selector that means only parts of the field with the neurons in inside the mask will be saved:
    if settings['getSpecificROI']==True:
        selector = np.ones(storage.data.shape,dtype=np.bool)
        for thisFileGet in settings['vfileInNamesRG']:
            selector[storage.get('thresholdSigLab_'+thisFileGet[0])==1]=False
        selector[storage.get('mask')==0]=True
    else:
        selector = np.zeros(storage.data.shape,dtype=np.bool)
    # Save space?
    for i in range(3):
        tep = field[:,:,:,i]
        tep[selector] = 0
    nrrd2.write(settings['vfieldNamePre']+"_X.nrrd",field[:,:,:,0])
    nrrd2.write(settings['vfieldNamePre']+"_Y.nrrd",field[:,:,:,1])
    nrrd2.write(settings['vfieldNamePre']+"_Z.nrrd",field[:,:,:,2])
    return
    