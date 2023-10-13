'''
Created on 1 Dec 2016

@author: s1144899

This code is quite old and although it works I've noticed many problems in its efficiency.

It should be rewritten!

'''
import numpy as np
from nodeRepresentationClasses import voxMap
'''
def generateOutput(connToKeep,skelImg):
    outPut = np.zeros(skelImg.shape,dtype='uint8')
    for thisConn in connToKeep:
        voxList = thisConn.voxels
        startVox = thisConn.voxels[0]
        endVox = voxList[len(voxList)-1]
        outPut[startVox[0],startVox[1],startVox[2]]=255
        outPut[endVox[0],endVox[1],endVox[2]]=255
        for i in range(1,len(voxList)-1):
            thisVox = voxList[i]
            outPut[thisVox[0],thisVox[1],thisVox[2]]=125
    return outPut
'''


def getNextMax(nodesInt,connToKeep,minBranchLength):
    maxLength = 0
    nodesToDo = 0
    maxNode=False
    # Find the current maximum (longest shortest path):
    for n in nodesInt:
        if (nodesInt[n].bestpathLength>maxLength) and nodesInt[n].bestpathLength>=minBranchLength:
            maxLength = nodesInt[n].bestpathLength
            maxNode = nodesInt[n]
        if nodesInt[n].isIncluded == False and nodesInt[n].bestpathLength>=minBranchLength:
            nodesToDo +=1
    if (maxNode!=False):
        # Set the maximum's included nodes as included:
        for thisNode in maxNode.bestpathList:
            thisNode.isIncluded = True
        # Remove these nodes from anywhere they appear in the list:
        for n in nodesInt:
            thisNode = nodesInt[n]
            # if the node still needs to be included then we are interested in modifying the bestpathList to remove what we just added:
            i=0
            while i< len(thisNode.bestpathConn):
                # Only remove the connections that have both nodes already included:
                if thisNode.bestpathConn[i].startNode.isIncluded == True and thisNode.bestpathConn[i].endNode.isIncluded == True:
                    thisConn = thisNode.bestpathConn.pop(i)
                    #TODO: This is probably going to add this many times but it shouldn't matter too much)
                    # move this to a dictionary format!
                    connToKeep += [thisConn]
                    thisConn.keepIt = True
                    # Not sure why this is required...:
                    #thisConn.endNode.keptConn += [thisConn]
                    #thisConn.startNode.keptConn += [thisConn]
                    
                    thisNode.bestpathLength -= thisConn.length
                    #print "removing",thisConn.startNode.voxel," to ", thisConn.endNode.voxel
                else:
                    i+=1
    return nodesToDo

# function to add nodes to list by expanding out from this node (fristNode):
def addPotentialNodes(firstNode,listOfPotentialNodes):
    for thisConn in firstNode.directConn:
        if (thisConn.endNode==firstNode):
            nodeToAdd = thisConn.startNode
        elif(thisConn.startNode==firstNode):
            nodeToAdd = thisConn.endNode
        # Check that new node is not already in the list:
        stillAdd = True
        # if there is a bestpathLength in this node, check that this one is shorter if we will add it:
        if (nodeToAdd.bestpathLength>-1):
            if ((firstNode.bestpathLength + thisConn.length)>=nodeToAdd.bestpathLength):
                stillAdd = False
        # Add it in:
        if (stillAdd == True):
            nodeToAdd.bestpathList = firstNode.bestpathList + [nodeToAdd]
            nodeToAdd.bestpathConn = firstNode.bestpathConn + [thisConn]
            nodeToAdd.bestpathLength = firstNode.bestpathLength + thisConn.length
            listOfPotentialNodes.append(nodeToAdd)

def remakeMap(connToKeep,nodesVox):
    # Mark all nodes that are to be kept:
    for thisConn in connToKeep:
        for thisNode in thisConn.nodes:
            thisNode.dynDict['keepIt'] = True
    # Clean up:
    newMap = voxMap()
    for thisNode in nodesVox.getDict().values():
        if 'keepIt' in thisNode.dynDict and newMap.contains(thisNode.voxel)==False:
            newMap.put(thisNode.voxel,thisNode)
            newNeighbourList = []
            for adjNode in thisNode.neighbours:
                if 'keepIt' in nodesVox.get(adjNode).dynDict:
                    newNeighbourList.append(adjNode)
            thisNode.neighbours = newNeighbourList
            thisNode.updateNodeCode()
            thisNode.directConn = []
    # Only have direct connections along connections kept in:
    # BUT this will add too many to the list as thisConn has multiple entries...
    # This is kind or redundant anyway so commenting out:
    '''
    for thisConn in connToKeep:
        thisConn.endNode.directConn.append(thisConn)
        thisConn.startNode.directConn.append(thisConn)
    '''
    #TODO: We may also want to re-add any connections that are 2-nodes that are still in the skeleton
    return newMap

def pruneLinked(candidateCBLoc,nodesVox,nodesInt,minBranchLength,connList,minConnLength):
    candidateCBLoc = np.asarray(candidateCBLoc)
    
    for thisConn in connList:
        thisConn.keepIt = False
    
    # first set up node info:
    for thisNode in nodesInt.values():
        thisNode.bestpathConn = []
        thisNode.bestpathLength = -1
        thisNode.isIncluded = False
        #thisNode.keptConn = []
        
    # Build the longest Path
    # Start at CBNode:
    if np.array_equal(candidateCBLoc,-np.ones(3))==False:
        CBNode = nodesVox.get(candidateCBLoc)
        # start the list:
        CBNode.bestpathList = [CBNode]
        CBNode.bestpathLength = 0
        # nodes which have been fully explored (as the shortest path)
        #listOfConnectedNodes = []
        # nodes that are connected and need to be explored:
        listOfPotentialNodes = []
        # Keep adding from best in list:
        addPotentialNodes(CBNode,listOfPotentialNodes)
        #TODO: If slow, replace with a sorted dictionary.... (binary tree...):
        while (len(listOfPotentialNodes)>0):
            # get the best node:
            bestNode = listOfPotentialNodes[0]
            for thisNode in listOfPotentialNodes:
                if thisNode.bestpathLength<bestNode.bestpathLength:
                    bestNode = thisNode
            # add it to the connected nodes list and remove it from the potential nodes list.
            #listOfConnectedNodes.append(bestNode)
            listOfPotentialNodes.remove(bestNode)
            addPotentialNodes(bestNode,listOfPotentialNodes)
        
        # Get the Longest shortest path and add all nodes in the path before updating the paths in the remaining nodes:
        connToKeep = []
        numOfNodesLeft = getNextMax(nodesInt,connToKeep,minBranchLength)
        while numOfNodesLeft>0:
            numOfNodesLeft = getNextMax(nodesInt,connToKeep,minBranchLength)
        # Re-add any long connections not kept!
        for thisConn in connList:
            if thisConn.keepIt == False and thisConn.length > minConnLength:
                if thisConn.startNode.isIncluded==True and thisConn.endNode.isIncluded == True:
                    connToKeep.append(thisConn)
        return remakeMap(connToKeep,nodesVox)
    else:
        return {}