'''
Created on 2 Dec 2016

@author: s1144899
'''
class node:
    # a list of all paths to connected nodes, (how long it takes to get to them and HOW to get to them from this way using the shortest path.)
    # a list of all connectors connected to this node.
    # the voxel represented by this node
    '''
    fields:
    voxel - 3 int array of voxel pos.
    nodeType - u: undefined
               e: end point (1 neighbour)
               j: junction (>2 neighbours)
               l: link (2 neighbours)
               p: point (no neighbours)
    neighbours - array of neighbours
    label - integer key of labelled image
    intID - position in keyNodeDict.
    '''
    def __init__(self,voxelIn,neighboursIn,labelIn):
        self.voxel = voxelIn
        self.neighbours = neighboursIn
        self.updateNodeCode()
        self.label = labelIn
        # For later:
        self.linkedUp = False
        self.dynDict = {}
        if self.nodeType == 'e' or self.nodeType == 'j':
            self.directConn = []
    def addDirectConnection(self,connIn):
        self.directConn.append(connIn)
    def updateNodeCode(self):
        thisSum = len(self.neighbours)
        nodeType = 'u' # undefined
        # create the node:
        if thisSum==1:
            nodeType = 'e' # end
        elif thisSum>2:
            nodeType = 'j' # junction
        elif thisSum==2:
            nodeType = 'l' # link
        elif thisSum==0:
            nodeType = 'p' # point
        self.nodeType = nodeType
        
class voxMap:
    def __init__(self):
        self.clear()
    def get(self,pos):
        return self.thatDict[str(pos)]
    def put(self,pos,node):
        self.thatDict[str(pos)] = node
    def clear(self):
        self.thatDict = {}
    def getDict(self):
        return self.thatDict
    def contains(self,pos):
        return str(pos) in self.thatDict