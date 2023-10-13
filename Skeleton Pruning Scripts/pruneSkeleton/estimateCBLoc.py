'''
Created on 1 Dec 2016

@author: s1144899
'''
import numpy as np
# NOTE WE ASSUME WE HAVE ALREADY FIXED DISTANCE CHART!
def getCBLoc(nodesIn,distanceChart):
    # now done elsewhere:
    #distanceChart = np.max(distanceChart)-distanceChart
    bestLoc = np.zeros(3)
    bestVal = -100000
    for thisNode in nodesIn.values():
        thisVal = distanceChart[tuple(thisNode.voxel)]
        if thisVal>bestVal:
            bestLoc = thisNode.voxel
            bestVal = thisVal
    return bestLoc