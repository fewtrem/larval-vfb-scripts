'''
Created on 7 Dec 2015

@author: s1144899
'''
import  nrrd2, numpy as np, nrrd
from doLabeling import doLabeling
from thresholdNeurons import calculateThreshold
'''
settings - the settings...
storage - the storage object.
'''
def doNeuronSegmentation(settings,storage):
    print "Pipeline: Doing Segmentation..."
    # we will open all channels and get the scores....
    savedis = {}
    for thisFileGet in settings['vfileInNamesRG']:
        print "Pipeline: Channel: ",thisFileGet[0]
        thresholdSigLabRef = 'thresholdSigLab_'+thisFileGet[0]
        # 0+150 = 150MB
        # do the labelling:
        labeledImg, nomIds = doLabeling(settings,storage,thresholdSigLabRef)
        # labeledImg NOT MASKED YET!
        savedis["LI_"+thisFileGet[0]] = labeledImg
        savedis["NID_"+thisFileGet[0]] = nomIds
        # save this version of the labelled image for identifying neurons later:
        if settings['vsaveLabels'] == True:
            nrrd2.write(settings['vlabelsNamePre']+thisFileGet[0]+".nrrd",labeledImg)
    savedis['set']=True
    return savedis
    # get the final score for each neuron (write it out with CoM):

# Combine the ROIs of segmented neurons:
def makeCombinedROI(settings,storage):
    print "Pipeline: Combining segmented neurons: "
    thisDataN = np.zeros(storage.data.shape,dtype=np.uint8)
    for thisFileGet in settings['vfileInNamesRG']:
        thisDataN[storage.get('thresholdSigLab_'+thisFileGet[0])==1]=1
    # ALSO APPLY MASK!!
    thisDataN[storage.get('mask')==0] = 0
    return thisDataN
    print "Pipeline: Done combining segmented neurons: "
