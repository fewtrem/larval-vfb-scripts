'''
Created on 1 Dec 2016

@author: s1144899
'''
import numpy as np
        
class connector:
    # a list of voxels involved
    # the two nodes that are joined by this connector 
    # the length of the connector
    def __init__(self,startNode,dimL):
        self.startNode = startNode
        self.endNode = None
        self.length = 0
        # dimension lengths
        self.dimL = dimL
        self.nodes = [startNode]
        startNode.addDirectConnection(self)
        
    def addNode(self,nodeIn):
        self.nodes.append(nodeIn)
        #Update the length:
        self.addExtraLength()
        
    def setEndNode(self,nodeIn):
        self.endNode = nodeIn
        self.nodes.append(nodeIn)
        # update the length:
        self.addExtraLength()
        nodeIn.addDirectConnection(self)
        
    # for later:
    def addExtraLength(self):
        oldV = np.array(self.nodes[len(self.nodes)-2].voxel)
        newV = np.array(self.nodes[len(self.nodes)-1].voxel)
        # Erm... pythag..!
        self.length += np.sqrt(np.sum(np.square((oldV-newV)*self.dimL)))
        
