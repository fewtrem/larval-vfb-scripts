'''
Created on 23 May 2017

@author: s1144899


This takes as input the pruneskel representation NOT the DR rep!  But can easily be changed - 
see notebook bumber 4 for CBNonCB Results! and "finalModelEvaluation" which is VERY similar.
also:
/afs/inf.ed.ac.uk/user/s11/s1144899/PhD/Python Projects/ml2017/ipythonResultsCBNonCB/finalModelEvaluationMethod2.py


'''
import numpy as np
def getCBLoc(settings,mapIn,thisSpread,cnnModel,refImg):
    lowestVox = getLowestVoxel(mapIn.getDict().values(),thisSpread)
    # get the paths out and the voxels to do ML on:
    allPathsOut,voxelsToCheck = getPathsOut(settings,mapIn,lowestVox,thisSpread)
    # do the ML:
    getMLResults(settings,cnnModel,voxelsToCheck,refImg)
    # get the dict:
    cBDict = getDict(settings,refImg.shape,voxelsToCheck,thisSpread)
    return allPathsOut,cBDict


def getLowestVoxel(voxListIn,thisSpread):
    bestVox = None
    bestScore = 10000
    for thisVox in voxListIn:
        thisScore = thisSpread[tuple(thisVox.voxel)]
        if thisScore<bestScore:
            bestVox = thisVox
            bestScore = thisScore
    return bestVox
# create paths to end points from this central voxel:
def getPathsOut(settings,voxMap,lowestVox,thisSpead,updateSpread = True):
    voxListIn = voxMap.getDict().values()
    # blank used but also get brain spread value for each voxel:
    for thisVox in voxListIn:
        thisVox.usedInA0 = False
    if updateSpread == True:
        for thisVox in voxListIn:
            thisVox.spreadPos = thisSpead[tuple(thisVox.voxel)]
    # starting path and list of all current paths:
    paths = [[lowestVox]]
    # paths that are done:
    keepPaths = []
    # ALSO get a list of all voxels that we want to check for CBLoc:
    voxelsToCheck = []
    # keep adding whilst we can:
    while len(paths)>0:
        newPaths = []
        # iterate over ends of paths:
        for thisPath in paths:
            # modified in this loop level flag:
            modifiedPath = False
            # check neighbour voxels:
            for thisNeighPos in thisPath[-1].neighbours:
                thisNeigh = voxMap.get(thisNeighPos)
                # if not used then modify path:
                if thisNeigh.usedInA0 == False:
                    # add new path:
                    newPaths.append(list(np.copy(thisPath))+[thisNeigh])
                    # set flags:
                    thisNeigh.usedInA0 = True
                    modifiedPath = True
                    # add to list of ML voxels if required:
                    if thisNeigh.spreadPos >=settings['threshForCBChecking']:
                        voxelsToCheck.append(thisNeigh)
            # if done then send to done list:
            if modifiedPath == False:
                keepPaths.append(thisPath)
        # update:
        paths = newPaths
    return keepPaths,voxelsToCheck

from CB_Cube import getVoxelRep
def getMLResults(settings,cnnMod,voxelsToCheck,reformatIn):
    # get the local proj:
    toTest = np.zeros((len(voxelsToCheck),settings['CBNonCB_shape'][0],settings['CBNonCB_shape'][1]))
    for nzCi in range(len(voxelsToCheck)):
        nzC = voxelsToCheck[nzCi].voxel
        cube = getVoxelRep(nzC,reformatIn,{'boundsWidth':settings['CBNonCB_boundWidth']})
        toTest[nzCi,:]=np.max(cube,axis=2)    
    # do the ML:
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
    for nzCi in range(len(voxelsToCheck)):
        voxelsToCheck[nzCi].mlResult = resultsF[nzCi]

from scipy import ndimage
def getDict(settings,skelShape,voxelsToCheck,thisSpread):
    print "  Outputting points for labelling:"
    # now let's output it for labelling:
    writeOnLocs = np.zeros(skelShape,dtype=np.bool)
    cubeDim = np.array(settings['CBNonCB_cubeDim'])
    for thisVoxel in voxelsToCheck:
        if thisVoxel.mlResult>=settings['CBNonCB_thresh']:
            thisPoint = np.array(thisVoxel.voxel)
            minV = thisPoint-cubeDim
            maxV = thisPoint+cubeDim+1
            minV[minV<0]=0
            writeOnLocs[minV[0]:maxV[0],minV[1]:maxV[1],minV[2]:maxV[2]]=True
    print "  Doing labelling:"
    # create the output CB Dict:
    cBDict = {}
    rep = ndimage.label(writeOnLocs)
    # first add the points in the skeleton:
    for thisVoxel in voxelsToCheck:
        if thisVoxel.mlResult>=settings['CBNonCB_thresh']:
            cBKey = rep[0][tuple(thisVoxel.voxel)]
            if cBKey in cBDict:
                cBDict[cBKey]['voxList'].append(thisVoxel)
            else:
                cBDict[cBKey] = {'voxList':[thisVoxel]}
                
    # get the Centre of mass and distance chart values:
    for cBKey in cBDict:
        forMean = []
        for vi in range(len(cBDict[cBKey]['voxList'])):
            forMean.append(cBDict[cBKey]['voxList'][vi].voxel)
        cBDict[cBKey]['com'] = np.mean(np.asarray(forMean),axis=0)
        # Get the distance from the border:
        cBDict[cBKey]['distChart'] = thisSpread[tuple(np.round(cBDict[cBKey]['com']).astype(np.int))]
    return cBDict