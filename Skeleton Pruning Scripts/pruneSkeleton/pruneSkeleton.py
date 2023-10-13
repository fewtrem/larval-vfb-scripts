'''
Created on 1 Dec 2016

@author: s1144899

Simplify it!
'''
from nodeRepresentation import getNodeRep
from linkedRepresentation import linkUp
from estimateCBLoc import getCBLoc
from pruneLinked import pruneLinked
import numpy as np
def pruneSkeleton(settings,skelImg,labelImg,distanceChart):
    skelImgPadded = np.pad(skelImg,1,'constant')
    maxNo = np.max(labelImg)
    mapN,dictKN = getNodeRep(skelImgPadded,labelImg,maxNo)
    mapN2 = {}
    for x in range(1,maxNo+1):
        connList = linkUp(mapN[x],dictKN[x],settings['voxelDims'])
        candidateCBLoc = getCBLoc(dictKN[x],distanceChart)
        mapN2[x] = [pruneLinked(candidateCBLoc,mapN[x],dictKN[x],settings['minBranchLength'],connList,settings['minConnLength']),candidateCBLoc]
    return  mapN2