'''
Created on 6 Jun 2017

@author: s1144899
'''
from getCBFunc import getBestCBLoc
from pruneSkeleton.nodeRepresentation import getNodeRep
from pruneSkeleton.linkedRepresentation import linkUp
from pruneSkeleton.pruneLinked import pruneLinked
from pruneSkeleton.pathsOut import getCBLoc
import numpy as np,pickle
TUBEDIR = 'tubeDir'
POSITION = 'position'
SPREADPOS = 'spreadPos'
NEIGHBOURS = 'neigbours'
NODETYPE = 'nodeType'
MLRESULT = 'mlResult'
TUBESCORE = 'tubeScore'
LAB = "**LAB**"
# convert rep to dictionary to save it independent of the class:
def saveMapFormat(mapIn):
    voxelListOut = []
    for thisVox in mapIn.getDict().values():
        thisVoxOut = {POSITION:thisVox.voxel,
                      SPREADPOS:thisVox.spreadPos,
                      NEIGHBOURS:thisVox.neighbours,
                      NODETYPE:thisVox.nodeType,
                      MLRESULT:None,
                      TUBESCORE:None,
                      TUBEDIR:None}
        for addName in [MLRESULT,TUBEDIR,TUBESCORE]:
            if addName in thisVox.__dict__:
                thisVoxOut[addName]=thisVox.__dict__[addName]
        voxelListOut.append(thisVoxOut)
    return voxelListOut
def makeCBDictSaveable(cBData):
    for cBKey in cBData:
        newVoxList = []
        for thisVox in cBData[cBKey]['voxList']:
            newVoxList.append(thisVox.voxel)
        cBData[cBKey]['voxList'] = newVoxList
def pruneSkeleton(settings,skelImg,labelImg,refImg,distanceChart,cnnModel,outFilePath):
    firstDer = gT.getFirstDer(settings,labelImg>0)
    skelImgPadded = np.pad(skelImg,1,'constant')
    maxNo = np.max(labelImg)
    mapN,dictKN = getNodeRep(skelImgPadded,labelImg,maxNo)
    for x in range(1,maxNo+1):
        print "  Label:",x
        if len(mapN[x].getDict().values())>0:
            # get the connection list:
            connList = linkUp(mapN[x],dictKN[x],settings['voxelDims'])
            # get a candidate CB location [x,y,z]:
            allPathsOut,cBData = getCBLoc(settings,mapN[x],distanceChart,cnnModel,refImg)
            candidateCBLoc = getBestCBLoc(cBData,mapN[x],dictKN[x].values(),allPathsOut)
            pruneRes = pruneLinked(candidateCBLoc[1],mapN[x],dictKN[x],settings['minBranchLength'],connList,settings['minConnLength'])
            makeCBDictSaveable(cBData)
            output = {'prunedSkel':saveMapFormat(pruneRes),
                      'cBData':cBData}
            thisOutFilePath = outFilePath.replace(LAB,str(x))
            fO = open(thisOutFilePath,'w')
            pickle.dump(output,fO)
            fO.close()
    return
