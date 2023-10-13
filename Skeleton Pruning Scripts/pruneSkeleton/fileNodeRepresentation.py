'''
Created on 2 Dec 2016

@author: s1144899
'''
nodesListKey = "nodesList"
voxelKey = "voxel"
neighboursKey = "neighbours"
labelKey = "label"
cBLocKey = "cbLoc"

import pickle
from nodeRepresentationClasses import node,voxMap
def saveNodeRep(mapNA,cBLocA,fileLoc):
    outDictA = {}
    for x in mapNA:
        mapN = mapNA[x]
        cBLoc = cBLocA[x]
        outDict = {}
        outDict[cBLocKey]=cBLoc
        outDict[nodesListKey] = {}
        for thisNode in mapN.getDict().values():
            outDict[nodesListKey][str(thisNode.voxel)] = {voxelKey:thisNode.voxel,
                                                       neighboursKey:thisNode.neighbours,
                                                       labelKey:thisNode.label}
        outDictA[x] = outDict
    fOut = open(fileLoc,'w')
    pickle.dump(outDictA,fOut)
    fOut.close()
    
def loadNodeRep(fileLoc):
    fIn = open(fileLoc)
    inDictA = pickle.load(fIn)
    fIn.close()
    mapNA = {}
    cBLocA = {}
    for x in inDictA:
        inDict = inDictA[x]
        cBLoc = inDict[cBLocKey]
        mapN = voxMap()
        for thisNode in inDict[nodesListKey].values():
            newNode = node(thisNode[voxelKey],thisNode[neighboursKey],thisNode[labelKey])
            mapN.put(str(newNode.voxel),newNode)
        mapNA[x] = mapN
        cBLocA[x] = cBLoc
    return mapNA,cBLocA
        
    