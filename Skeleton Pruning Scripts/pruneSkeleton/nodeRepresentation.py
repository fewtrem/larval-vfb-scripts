'''
Created on 2 Dec 2016

@author: s1144899
'''
import numpy as np
from nodeRepresentationClasses import node,voxMap
        
# faster way to get order of nodes - as the images are super sparse!
def getNodeRep(skelImgPadded,labelledImg,labelledImgMax):
    allNZ = np.transpose(np.asarray(np.nonzero(skelImgPadded)))
    # initialised dictionaries:
    voxMapDict = {}
    keyNodeDict = {}
    for i in range(1,labelledImgMax+1):
        voxMapDict[i] = voxMap()
        keyNodeDict[i] = {}
    # go through all non-zeros:
    for paddedPos in allNZ:
        actualPos = np.asarray(paddedPos)-1
        # get the label
        label = labelledImg[tuple(actualPos)]
        #TODO: remove
        if label==0:
            print "zero label at:",actualPos
        # get the neighbours:     
        seg = skelImgPadded[paddedPos[0]-1:paddedPos[0]+2,paddedPos[1]-1:paddedPos[1]+2,paddedPos[2]-1:paddedPos[2]+2]
        adjListIncThis = np.transpose(np.asarray(np.nonzero(seg)))
        # update the positions in adjacency to actual values and remove this node:
        adjList=[]
        for adj in adjListIncThis:
            adjPos = adj-1+actualPos
            if np.array_equal(adj,np.array([1,1,1]))==False:
                if labelledImg[tuple(adjPos)]==label:
                    adjList.append(adjPos)
        # node order:
        thisSum = len(adjList)
        # Put the nodes in the lists and create their objects:
        # Actually create the new node:
        thisNode = node(actualPos,adjList,label)
        voxMapDict[label].put(actualPos,thisNode)
        if thisSum==1 or thisSum>2:
            # get position to put in list:
            thisListPos = len(keyNodeDict[label])
            thisNode.intID = thisListPos
            # add to the list / map:
            keyNodeDict[label][thisListPos] = thisNode
    return voxMapDict,keyNodeDict