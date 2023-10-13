'''
Created on 30 Jan 2017

@author: s1144899
'''
import numpy as np
def prePreOps(settings):
    return
## pre ops to smoothe the whole image!:
def preOps(imgIn,storeKey,settings):
    return
# A function to get the cuboid region around a point:
# Based on "randomWarps.py":
# Assumes that at least some of the image will be displayed!
def getVoxelRep(ci,imgIn,settings):
    boundsWidth = settings['boundsWidth']
    sN = np.array(boundsWidth,dtype=np.int)
    outputShape = sN*2+1
    outputHere = np.zeros(outputShape,dtype=np.int)
    ci = np.array(ci).astype(np.int)
    sNL = ci-sN
    sNU = ci+sN+1
    returnRange = [[0,outputShape[0]],[0,outputShape[1]],[0,outputShape[2]]]
    for x in range(3):
        if sNL[x]<0:
            returnRange[x][0]=-sNL[x]
            sNL[x]=0
        diff = sNU[x]-imgIn.shape[x]
        if diff>0:
            returnRange[x][1]=outputShape[x]-diff
            sNU[x]=imgIn.shape[x]
    selector = imgIn[sNL[0]:sNU[0],sNL[1]:sNU[1],sNL[2]:sNU[2]]
    outputHere[returnRange[0][0]:returnRange[0][1],returnRange[1][0]:returnRange[1][1],returnRange[2][0]:returnRange[2][1]] = selector
    return outputHere