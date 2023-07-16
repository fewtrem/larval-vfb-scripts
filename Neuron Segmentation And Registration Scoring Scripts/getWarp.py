'''
Created on 28 Aug 2016

@author: s1144899

This uses fast methods to get the warp field:

'''
#import resource
from scipy import ndimage
import ctypes, numpy as np, os
#import time
dir_path = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.cdll.LoadLibrary(os.path.join(os.path.join(dir_path,'CFunc'),'sumConv.so'))
sumConv = lib.sumConv
lib2 = ctypes.cdll.LoadLibrary(os.path.join(os.path.join(dir_path,'CFunc'),'sumProgMeanCov.so'))
cSumProg = lib2.sumProg
'''
Returns the low-res field of reduced shape + [3] dims for directions, with NO borders added, but the inner convB+exploreB will NOT be occupied.
'''
def getWarpField(tempImage,floatImage,settings):
    print "Pipeline:   Starting Scoring Round..."
    skipdips = settings['skipdips']
    convB = settings['convB']
    exploreB = settings['exploreB']
    
    # Slicing
    tempSlice = np.copy(tempImage[::skipdips[0],::skipdips[1],::skipdips[2]])
    floatSlice = np.copy(floatImage[::skipdips[0],::skipdips[1],::skipdips[2]])
    # Functions for doing Conv's:

    def doConv(inSeg):
        sd = np.std(inSeg)
        if sd != 0:
            divSdev = 1/sd
        else:
            divSdev = 1
        return (np.mean(inSeg)*divSdev,divSdev,np.sum(np.multiply(inSeg,inSeg))*(divSdev*divSdev),np.sum(inSeg)*divSdev)

    def getConvs(inArray):
        outArray = np.zeros(list(inArray.shape)+[4],dtype=np.double)
        tDims = inArray.shape
        for x in range(convB[0],tDims[0]-convB[0]):
            for y in range(convB[1],tDims[1]-convB[1]):
                for z in range(convB[2],tDims[2]-convB[2]):
                    outArray[x,y,z,:] = doConv(inArray[x-convB[0]:x+convB[0]+1,y-convB[1]:y+convB[1]+1,z-convB[2]:z+convB[2]+1].astype(np.double))
        return outArray

    # Store the means, s.devs and the sums:
    convTempStore = getConvs(tempSlice)
    convFloatStore = getConvs(floatSlice)
    # Exploring the space
    convMax = np.prod(np.asarray(convB)*2+1)
    dimsAsLong = np.asarray(tempSlice.shape).astype(np.long)
    convWidthAsLong = np.asarray(convB).astype(np.long)
    storageArray = np.zeros(list(tempSlice.shape)+[exploreB[0]*2+1,exploreB[1]*2+1,exploreB[2]*2+1],dtype=np.int32,order='C')
    # Roll the FLOAT around so we can compare different TEMPLATES to it
    # Store ex,ey,ez etc. as directions FROM TEMPLATE TO FLOAT voxels....
    # So we need to fill later by just adding the appropriate ex,ey,ez etc.
    print "Pipeline:     Performing shifts and sums..."
    for ex in range(-exploreB[0],exploreB[0]+1):
        for ey in range(-exploreB[1],exploreB[1]+1):
            for ez in range(-exploreB[2],exploreB[2]+1):
                thisFloatShifted = np.roll(floatSlice,-ex,0)
                thisFloatShifted = np.roll(thisFloatShifted,-ey,1)
                thisFloatShifted = np.roll(thisFloatShifted,-ez,2)
                tDiff = np.ascontiguousarray(np.multiply(thisFloatShifted.astype(np.uint16),tempSlice.astype(np.uint16)))
                sumOutData =  np.ascontiguousarray(np.zeros(tempSlice.shape,dtype=np.int32))
                cSumProg(ctypes.c_void_p(tDiff.ctypes.data),
                 ctypes.c_void_p(dimsAsLong.ctypes.data),
                 ctypes.c_void_p(convWidthAsLong.ctypes.data),
                 ctypes.c_void_p(sumOutData.ctypes.data))
                storageArray[:,:,:,ex+exploreB[0],ey+exploreB[1],ez+exploreB[2]] = sumOutData
    print "Pipeline:     Done shifts and sums..."
    # Calculate minimas:
    dimsH = np.asarray(storageArray.shape)[:3].astype(np.long)
    exploreH = np.asarray(exploreB).astype(np.long)
    convFloatStore = np.ascontiguousarray(convFloatStore)
    convTempStore = np.ascontiguousarray(convTempStore)
    storageArray = np.ascontiguousarray(storageArray)
    outData2 = np.ascontiguousarray(np.zeros(np.asarray(exploreB)*2+1,dtype=np.double))
    minimas = np.zeros(list(dimsH)+[3],dtype=np.int8)
    # Update the minimas with the other values:
    print "Pipeline:     Getting scores and finding minima..."
    for x in range(convB[0]+exploreB[0],dimsAsLong[0]-convB[0]-exploreB[0]):
        for y in range(convB[1]+exploreB[1],dimsAsLong[1]-convB[1]-exploreB[1]):
            for z in range(convB[2]+exploreB[2],dimsAsLong[2]-convB[2]-exploreB[2]):
                sumConv(ctypes.c_void_p(storageArray.ctypes.data),
                 ctypes.c_void_p(dimsAsLong.ctypes.data),
                 ctypes.c_void_p(exploreH.ctypes.data),
                 ctypes.c_void_p(convTempStore.ctypes.data),
                 ctypes.c_void_p(convFloatStore.ctypes.data),
                 ctypes.c_int(x),ctypes.c_int(y),ctypes.c_int(z),ctypes.c_int(int(convMax)),
                 ctypes.c_void_p(outData2.ctypes.data))
                minimas[x,y,z,:]=np.asarray(np.unravel_index(np.argmin(outData2),np.asarray(exploreB)*2+1))-exploreB
    minimas[:,:,:,0] = minimas[:,:,:,0]*skipdips[0]
    minimas[:,:,:,1] = minimas[:,:,:,1]*skipdips[1]
    minimas[:,:,:,2] = minimas[:,:,:,2]*skipdips[2]
    print "Pipeline:     Done scores and finding minima"
    #print  "Alignopolis: Using ",(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000),"MB"
    print "Pipeline:   Done Scoring Round"
    return minimas
'''
Returns field of size tempImage + [3] based on fieldT input!
'''
def smoothIntoLargeField(settings,fieldT,tempImage):
    skipdips = settings['skipdips']
    print "Pipeline: Smoothing..."
    convVals = np.multiply(settings['convValsMult'],np.divide(1.0,settings['vScalerXYZ']))
    # Smoothing:
    #fieldT = minimas
    origDimW = tempImage.shape
    binsW = np.zeros(origDimW,dtype=np.bool)
    binsW[::skipdips[0],::skipdips[1],::skipdips[2]] = 1
    # A 2.5GB array:
    convBinW = ndimage.gaussian_filter(binsW.astype('float32'),convVals,mode='constant',cval=0.0)
    del binsW
    convBinW[convBinW==0]=1
    outPutW = np.zeros(list(origDimW)+[3],dtype=np.int8)
    # save space by doing one dimension at a time:
    for i in range(3):
        convInW = np.zeros(origDimW,dtype='float32')
        convInW[::skipdips[0],::skipdips[1],::skipdips[2]] = fieldT[:,:,:,i].astype('float32')
        convInW = ndimage.gaussian_filter(convInW,convVals,mode='constant',cval=0.0)
        outPutW[:,:,:,i]=np.round(np.divide(convInW,convBinW))
    print "Pipeline: Done Smoothing"
    return outPutW.astype(np.int8)
