'''
Created on 7 Dec 2015

@author: s1144899
'''
#from colours import colourArray
import numpy as np
from scipy import ndimage
import copy
import nrrd
def getNeuronScores(settings,labeledImg,nomIds,scoreField,storage,filetype):
    #ROI = settings['scoringROI']
    print "Pipeline:   Getting Neuron Scores..."
    multiplierA = np.ones((1,3))
    multiplierA[0,:] = settings['vScalerXYZ']
    scoresR = {}
    if settings['vsaveVoxelScores'] == True:
        forExport = np.zeros(labeledImg.shape,dtype='uint8')
    else:
        forExport = None
    # Recall that nomIds is max+1 of neuron labels!
    for Ni in range(1,nomIds):
        print "Pipeline:   Scoring neuron ",Ni," out of ",(nomIds-1)
        newNeuron={'id':copy.deepcopy(Ni),
                   'sig':copy.deepcopy(filetype)}
        # get the Selector:
        thisSelector = labeledImg==Ni
        # PREMASK:
        # store Centre of Mass:
        cOM = ndimage.measurements.center_of_mass(thisSelector)
        cOM = [cOM[1],cOM[0],cOM[2]]
        newNeuron['cOM']=cOM
        newNeuron['vol'] = np.sum(thisSelector)
        # POSTMASK:    
        thisSelector[storage.get('mask')==0]=0
        # store neuropile volume
        newNeuron['inVol'] = np.sum(thisSelector)
        inCoM = ndimage.measurements.center_of_mass(thisSelector)
        inCoM = [inCoM[1],inCoM[0],inCoM[2]]
        newNeuron['inCOM'] = inCoM
        # calculate the score:
        # get the hypoteneuse SQUARED of the direction!
        thisField = scoreField[thisSelector,:]
        thisField = np.sum(np.power(thisField*multiplierA,2).astype('float'),axis=1)
        # histogram of directions (256 is limit)
        hist = np.histogram(thisField,256,(0,256))
        # convert to cumulative sum:
        scoresH = np.cumsum(hist[0])/float(len(thisField))
        if settings['vsaveVoxelScores'] == True:
            thisField = thisField/settings['vDivisor']
            thisField[thisField>255] = 255
            forExport[thisSelector] = thisField.astype('uint8')
        newNeuron['scoresH'] = scoresH
        # score converter:
        newNeuron['singleScore'] = scoresH[settings['vhistScore']]
        scoresR[Ni]=newNeuron
    # save an NRRD of the voxel scores if required:
    if settings['vsaveVoxelScores'] == True:
        nrrd.write(settings['vvoxelScoreNamePre']+filetype+".nrrd",forExport)
    return scoresR
