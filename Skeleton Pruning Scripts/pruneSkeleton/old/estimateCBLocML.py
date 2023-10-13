'''
Created on 20 Feb 2017

@author: s1144899

Use the ML version to estimate the CBLoc.

'''
'''
settings = {}
settings['CBNonCB_batchSize'] = 2000
# model info:
settings['CBNonCB_modelSetup'] = {'Layers':[['conv',[15,15, 1, 32],0.002,0.001,[1, 2, 2, 1],[1, 2, 2, 1]],
                                                    ['conv',[10,10, 32, 32],0.002,0.001,[1, 2, 2, 1],[1, 2, 2, 1]],
                                                    ['conv',[5,5, 32, 32],0.02,0.01,[1, 2, 2, 1],[1, 2, 2, 1]],
                                                    ['neural',100,0.02,0],
                                                    ['linear',2,0.2,0]]}
settings['CBNonCB_shape'] = [41,41]
settings['CBNonCB_boundWidth'] = [20,20,12]
settings['CBNonCB_savedModelPath'] = "/media/s1144899/JaneliaBlue/CBNonCBTrainingSets/cnn2/Advanced/cnnInc"
# threshold in probability is CB:
settings['CBNonCB_thresh'] = 0.5
# draw out the CBs with points of cubes this border width for labelling!
settings['CBNonCB_cubeDim'] = [3,3,3]
'''

import cBNonCB_network as net
import cBNonCB_errorFuncs as err
from cBNonCB_cube import getVoxelRep
from scipy import ndimage
import numpy as np
def getCBs(settings,skelIn,labelIn,reformatIn,maskSpreadIn):
    # Set up a class to store out model for now:
    class cnnMod:
        def __init__(self):
            return
    sessionType = {'type':'interactive'}
    # dummy dataloader just gives shape of input for model construction:
    class getShapeOnly:
        def __init__(self):
            return
        def getShape(self):
            return settings['CBNonCB_shape']
    cnnMod.dataProc = getShapeOnly()
    # use CrossEntropy
    cnnMod.errorFunc = err.crossEntropy()
    # build model using TF:
    cnnMod.netProc = net.networkProc('cnn',cnnMod.dataProc,cnnMod.errorFunc,
                                         settings['CBNonCB_modelSetup'],
                                         'convNet',sessionType)
    # restore the model:
    cnnMod.netProc.saver.restore(cnnMod.netProc.sess,settings['CBNonCB_savedModelPath'])
    # get values to feed to model from skeleton:
    nzSkel = np.array(np.nonzero(skelIn)).transpose()
    print nzSkel.shape[0]," points"
    toTest = np.zeros((nzSkel.shape[0],settings['CBNonCB_shape'][0],settings['CBNonCB_shape'][1]))
    for nzCi in range(nzSkel.shape[0]):
        nzC = nzSkel[nzCi]
        cube = getVoxelRep(nzC,reformatIn,{'boundsWidth':settings['CBNonCB_boundWidth']})
        toTest[nzCi,:]=np.max(cube,axis=2)
    # get the results:
    resultsF = np.zeros((toTest.shape[0],1),dtype=np.float32)
    # split into batches of batchSize
    for i in np.arange(0,toTest.shape[0],settings['CBNonCB_batchSize']):
        # this takes a reasonable amount of time (i.e. a few seconds):
        batch = {cnnMod.netProc.input:toTest[i:i+settings['CBNonCB_batchSize']],cnnMod.netProc.keep_prob:1.0}
        results = cnnMod.netProc.y.eval(feed_dict=batch)
        resultsE = np.exp(np.asarray(results))
        resultsG = (resultsE/np.tile(np.sum(resultsE,axis=1),(2,1)).transpose())[:,0]
        resultsG = resultsG.reshape((resultsG.shape[0],1))
        resultsF[i:i+settings['CBNonCB_batchSize']] = resultsG
    # get above threshold:
    selector = resultsF>settings['CBNonCB_thresh']
    selector = selector[:,0]
    toDraw = nzSkel[selector,:]
    toDrawP = resultsF[selector]
    # now let's output it for labelling:
    writeOnLocs = np.zeros(reformatIn.shape,dtype=np.bool)
    cubeDim = settings['CBNonCB_cubeDim']
    for thisPoint in toDraw:
        writeOnLocs[thisPoint[0]-cubeDim[0]:thisPoint[0]+cubeDim[0]+1,
                    thisPoint[1]-cubeDim[1]:thisPoint[1]+cubeDim[1]+1,
                    thisPoint[2]-cubeDim[2]:thisPoint[2]+cubeDim[2]+1]=True
    # create the output CB Dict:
    cBDict = {}
    rep = ndimage.label(writeOnLocs)
    # first add the points in the skeleton:
    for pI in range(len(toDraw)):
        thisPoint = toDraw[pI]
        thisProb = toDrawP[pI]
        cBKey = rep[0][tuple(thisPoint)]
        thisLab = labelIn[tuple(thisPoint)]
        if cBKey in cBDict:
            cBDict[cBKey]['voxList'].append([thisPoint,thisProb])
            cBDict[cBKey]['labelDict'][thisLab]=True
        else:
            cBDict[cBKey] = {'voxList':[[thisPoint,thisProb]],
                             'labelDict':{thisLab:True}}
    # get the Centre of mass and distance chart values:
    for cBKey in cBDict:
        forMean = []
        for vi in range(len(cBDict[cBKey]['voxList'])):
            forMean.append(cBDict[cBKey]['voxList'][vi][0])
        cBDict[cBKey]['com'] = np.mean(np.asarray(forMean),axis=0)
        # Get the distance from the border:
        cBDict[cBKey]['distChart'] = maskSpreadIn[tuple(np.round(cBDict[cBKey]['com']).astype(np.int))]
    return cBDict
