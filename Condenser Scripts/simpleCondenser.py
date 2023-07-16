'''
Created on 29 Nov 2016

@author: s1144899

CHECK THE CORRECT VERSION IS USED OF THIS!
This is now run on an EDDIE BATCH JOB!

'''

import numpy as np
from scipy import ndimage
'''
Condense an image into points that represent it using projections.
imgIn - the image we are condensing
maskIn - mask
whiteIn - the white warp so we know the image's scope
maskPoints - points in the projections that are in the mask - for convenience, from getMaskArray
settings['2Dsdev'] = 5
settings['imgDimLengths'] = [1.0,1.0,1.707]
settings['skipFor2DPoints'] = [[10,5],[10,5],[7,7]]
settings['skipFor3DPointsSF'] = [10,10,7]
'''
def getMaskSelector2D(settings,maskIn):
    # Make it binary:
    maskIn[maskIn>0]=1
    # Store for mask projs:
    maskProjs = []
    sN = settings['skipFor2DPoints']
    # One proj at a time:
    for i in range(3):
        # do projections:
        thisProj = np.sum(maskIn.astype(np.float16),axis=i)>0
        # IMPORTANT: sample AFTER projecting!
        thisProj = thisProj[::sN[i][0],::sN[i][1]]
        # Append to array:
        maskProjs.append(thisProj)
    return maskProjs


def getMaskSelector3D(settings,maskIn):
    # Make it binary:
    maskIn[maskIn>0]=1
    sN = settings['skipFor3DPointsSF']
    # Simply return sampled array:
    return maskIn[::sN[0],::sN[1],::sN[2]]

def smootheIt(settings,imgIn):
    lengths = np.asarray(settings['imgDimLengths'])
    sdev = settings['2Dsdev']
    # smoothe the image and make binary:
    smoothedImg = (imgIn!=0).astype('float32')
    for i in range(settings['numSmoothings']):
        smoothedImg = ndimage.filters.gaussian_filter(smoothedImg, sdev/lengths, order=0, output=None, mode='constant', cval=0.0)#, truncate=3.0)
    # Re-adding truncation:
    smoothedImg[smoothedImg<settings['truncCutOff']] = 0
    return smoothedImg
'''
Convention is:
0: neither white nor signal
1: signal only - there should hardly any of these....(due to dilations probably some)
2: white space only
3: white space+signal.
'''
def make2DPointsSF(settings,imgIn,maskIn,whiteO,maskPoints):
    smoothedImg = smootheIt(settings,imgIn)
    # Make sure white in is only where mask is:
    whiteIn = whiteO.copy()
    whiteIn[maskIn==0]=0
    sN = settings['skipFor2DPoints']
    neuronPoints = []
    for i in range(3):
        # Get sparse neuron projs:
        neuronProj = np.sum(smoothedImg,axis=i)>0
        # Sample it:
        neuronProj = neuronProj[::sN[i][0],::sN[i][1]].astype(np.uint8)
        # Get sparse whitespace projs:
        whiteProj = np.sum(whiteIn,axis=i)>0
        # Sample it:
        whiteProj = whiteProj[::sN[i][0],::sN[i][1]].astype(np.uint8)*2
        # add the white and the neuronProj together:
        toGo = whiteProj+neuronProj
        toGo = toGo.astype(np.uint8)
        # finally, add to the list only the values in the mask and ravel:
        neuronPoints+=list(toGo[maskPoints[i]==1])
    return np.array(neuronPoints).astype(np.uint8)

def make3DPointsSF(settings,imgIn,maskIn,whiteIn,maskSelector):
    # Make sure white in is only where mask is:
    #whiteIn = whiteO.copy()
    #whiteIn[maskIn==0]=0
    smoothedImg = smootheIt(settings,imgIn)
    sN = settings['skipFor3DPointsSF']
    # Sample and theshold:
    neuronS = (smoothedImg[::sN[0],::sN[1],::sN[2]]>0).astype(np.uint8)
    # Get sparse whitespace projs:
    whiteB = whiteIn>0
    whiteB = whiteB[::sN[0],::sN[1],::sN[2]].astype(np.uint8)*2
    # add the white and the neuronProj together:
    toGo = whiteB+neuronS
    # finally, return only the values in the mask and ravel:
    neuronPoints=toGo[maskSelector==1]
    return neuronPoints.astype(np.uint8)