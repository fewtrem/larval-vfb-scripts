'''
Created on 7 Dec 2015

@author: s1144899
'''
import nrrd,itertools
import numpy as np
from scipy import ndimage
from getROIs import makeScoringRegionROI
'''
settings - the settings...

stores in storage:
[region required to save for scoring,
 what gets used in the neural segmentation,
 what gets labelled]
 Note that these are UNMASKED!
'''

def calculateThreshold(settings,thisDataN,nameIn):
    if nameIn in settings['thresholdValues']:
        thresh = settings['thresholdValues'][nameIn]                                            
    else:
        thresh = 0
        hist =  np.histogram(thisDataN,256,(0,256))
        thisCF = np.cumsum(hist[0])
        thisCF = thisCF/float(thisCF[-1])
        thresh = 0
        while thisCF[thresh] < settings['vthreshProp']:
            thresh += 1
        if thresh < settings['vAbsoluteMinThresh']:
            thresh = settings['vAbsoluteMinThresh']
        settings['thresholdValues'][nameIn] = thresh
    return thresh

def thresholdNeuronsForScoring(settings,storage2):
    print "Pipeline: Thresholding Neurons For Scoring..."
    for thisFileGet in settings['vfileInNamesRG']:
        print "Pipeline: Channel: ",thisFileGet[0]
        # 0+150 = 150MB
        thisFileName = thisFileGet[1]
        thisDataN = nrrd.read(thisFileName)[0]
        thresh = calculateThreshold(settings,thisDataN,thisFileGet[0])
        # get a dynamic threshold:
        print "Pipeline:   Thresholding at: ",thresh
        settings['threshUsed_'+thisFileGet[0]] = thresh
        # Do thresholding of this signal channel:
        thresholdSig = np.zeros(thisDataN.shape,dtype='uint8')
        thresholdSig[thisDataN<thresh]=0
        thresholdSig[thisDataN>=thresh]=1
        # Remove speckles:
        thresholdSig = makeScoringRegionROI(settings,thresholdSig)
        thresholdSigG = ndimage.binary_dilation(thresholdSig,iterations=settings['vsigIt'])
        # do cellbody identification across whole image:
        print "Pipeline:   Adding to Storage..."
        # save to an array:
        storage2.add('thresholdG_'+thisFileGet[0],thresholdSigG)
        storage2.add('thresholdSig_'+thisFileGet[0],thresholdSig)
        # loop through z to reduce memory consumption!
        del thresholdSig
        del thresholdSigG
        print "Pipeline:   Done Thresholding Channel"
    return

def thresholdNeuronsForLabelling(settings,storage2):
    print "Pipeline: Thresholding Neurons For Labelling..."
    for thisFileGet in settings['vfileInNamesRG']:
        thresholdSig = storage2.get('thresholdSig_'+thisFileGet[0])
        #thresholdG = storage2.get('thresholdG_'+thisFileGet[0])
        print "Pipeline: Channel: ",thisFileGet[0]
        # Copy the threshold and dilate it:
        #150+150 = 300MB
        thresholdSigLab = thresholdSig.copy()
        #(default 3 iterations)
        # SigG is what gets labelled (and used in scoring)
        # SigLab is what determines labelling...
        '''
        #300-150 = 150MB
        # now pack away the other one for later (saves a lot of space in memory!)
        threshShape = copy.deepcopy(thresholdSig.shape)
        thresholdSig = np.packbits(thresholdSig.reshape(np.prod(threshShape)).astype('int'))
        thresholdSig = np.unpackbits(thresholdSig)[0:np.prod(threshShape)].reshape(threshShape).astype('bool')
        '''
        # Expand the signal threshold by 3 to merge anything that might be left:
        xyStruct = np.zeros((3,3,3),dtype='bool')
        xyStruct[:,:,1] = ndimage.generate_binary_structure(2,1)
        for _ in itertools.repeat(1,settings['vneuronSep']):
            for _ in itertools.repeat(1,settings['vneuronSepxyE']):
                thresholdSigLab = ndimage.binary_dilation(thresholdSigLab,structure = xyStruct)
            thresholdSigLab = ndimage.binary_dilation(thresholdSigLab)
        # do cellbody identification across whole image:
        print "Pipeline:   Adding to Storage..."
        # save to an array:
        storage2.add('thresholdSigLab_'+thisFileGet[0],thresholdSigLab)
        # loop through z to reduce memory consumption!
        print "Pipeline:   Done Thresholding Channel"
    return