'''
Created on 1 Dec 2016

@author: s1144899
'''
import numpy as np
from linkedRepresentationClasses import connector
    

def nextVox(connIn,newNode,oldNode,nodesMap):
    doThis = True
    i = 0
    while(doThis==True):
        i+=1
        # add the voxel if a line:
        if newNode.nodeType == 'l':
            connIn.addNode(newNode)
            # Set to zero:
            newNode.linkedUp = True
            # go to next:
            adjList = newNode.neighbours
            # This should NEVER happen, but check anyway:
            if len(adjList)!=2:
                raise Exception('Inconsistency in connections', str(newNode.voxel)+' has '+str(len(adjList))+" instead of 2")
                doThis = False
            else:
                # in case oldPos is still there (i.e. is node) need to not choose it:
                newNodeH = None
                for adj in adjList:
                    if not(np.array_equal(adj,oldNode.voxel)):
                        newNodeH = nodesMap.get(adj)
                # Shuffle along:
                oldNode = newNode
                newNode = newNodeH
        # terminate the connection:
        else:
            connIn.setEndNode(newNode)
            doThis = False
        # This should never be met as all paths must go somewhere.... but let's keep a failsafe:
        if i>4000:
            print "ERROR - map to paths failed for voxel: ",newNode.voxel
            doThis = False

# Build the paths up for THIS label only:
#voxelmap,keynode dict, voxel dimensions
def linkUp(nodesMap,nodesInt,lengths):
    connectionList = []
    #dimension lengths:
    lengthsA = np.asarray(lengths)
    # Build the paths:
    for nf in nodesInt:
        thisNode = nodesInt[nf]
        # search the neighbours for the surrounding voxels to start new connections:
        adjList = thisNode.neighbours
        for adj in adjList:
            # Calculate the nonzero value:
            adjNode = nodesMap.get(adj)
            # Create the connection:
            # check adjacent is not a loop back already done!
            if adjNode.linkedUp!=True:
                thisConn = connector(thisNode,lengthsA)
                connectionList.append(thisConn)
                nextVox(thisConn,adjNode,thisNode,nodesMap)
        # Set this voxel to be zero now (not earlier as might be loops...)
        thisNode.linkedUp = True
    return connectionList