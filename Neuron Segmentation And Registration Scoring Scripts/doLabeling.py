'''
Created on 7 Dec 2015

@author: s1144899
'''
from scipy import ndimage
import numpy as np
import os,ctypes
dir_path = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.cdll.LoadLibrary(os.path.join(os.path.join(dir_path,'CFunc'),'uniqueVals.so'))
cUniqueVals = lib.uniqueVals
'''
SigLab - the labelling Sig - 
SigG - the actual Sig we will get the scores for 

'''
def doLabeling(settings,storage,sigLabKey):
    print "Pipeline:   Doing Labeling..."
    savedis = 1
    newRep=np.zeros(storage.data.shape,dtype='uint8')
    # + 300MB
    struct=ndimage.generate_binary_structure(3,2)
    rep = ndimage.label(storage.get(sigLabKey)==1,struct,output=np.int32)
    theFreq = np.zeros(rep[1]+1,dtype=np.int32)
    theFreq = np.ascontiguousarray(theFreq)
    sizeLoop = np.product(np.array(rep[0].shape))
    cUniqueVals(ctypes.c_void_p(rep[0].ctypes.data),
             ctypes.c_long(long(sizeLoop)),
             ctypes.c_void_p(theFreq.ctypes.data))
    for i in range(1,len(theFreq)):
        # remove small specles:
        if theFreq[i]>settings['vminVoxelsinNeuron'] and savedis<255:#vMaxSpecleSize
            if i!=0:
                newRep[rep[0]==i]=savedis
                savedis += 1
        if savedis>=255:
            print "Alignopolis: WARNING: Maximum number of neurons (254) reached"
    
    # -300MB
    return newRep, savedis
