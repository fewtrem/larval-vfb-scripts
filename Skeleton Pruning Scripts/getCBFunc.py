'''
Created on 6 Jun 2017

@author: s1144899
'''
import numpy as np
def getBestCBLoc(cBData,mapIn,nodeListIn,allPathsOut):
    bestCB = None
    bestLen = -1
    if len(cBData)==0:
        print "  --No CBs found--"
    for thisCB in cBData:
        thisLen = len(cBData[thisCB]['voxList'])
        if thisLen>bestLen:
            bestCB = cBData[thisCB]
            bestLen = thisLen
    if bestLen!=-1:
        for thisVox in mapIn.getDict().values():
            thisVox.bestCBScore = 0
        for thisCBVox in bestCB['voxList']:
            thisCBVox.bestCBScore = 1
        bestPathOutScore = 0
        bestPathOut = None
        for thisPathOut in allPathsOut:
            thisPathOutScore = 0
            for thisVox in thisPathOut:
                thisPathOutScore+=thisVox.bestCBScore
            if thisPathOutScore>bestPathOutScore:
                bestPathOut = thisPathOut
                bestPathOutScore = thisPathOutScore
        # get the END/JUNCTION point path that has the most of these CB voxels in.
        if bestPathOutScore > 0:
            if bestPathOut[-1].nodeType == 'e' or bestPathOut[-1].nodeType == 'j':
                print "  Best CB End returned at ",bestPathOut[-1].voxel
                return ["BestCBNearbyNode",bestPathOut[-1].voxel]
        # if there is not an end point then we will just try and find the end the old way:
        # get the best join point (node) if no CBs found / no ends:
    bestLoc = -np.ones(3)
    bestVal = -100000
    for thisNode in nodeListIn:
        thisVal = thisNode.spreadPos
        if thisVal>bestVal:
            bestLoc = thisNode.voxel
            bestVal = thisVal
    print "  Old method CB (lowest spread score skeleton voxel) returned at ",bestLoc
    return ["LowestSpread",bestLoc]