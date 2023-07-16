'''
Created on 28 Aug 2016

@author: s1144899

The storage class to store data:

'''
'''
Storage system with [old names]
[mask] mask from template
[thisDataN] the masked voxels for both R and G that we want to use to asses the scoring.
for R and G channels:
[thresholdSig_X] Threshold for what gets labelled Channel X
[thresholdSigLab_X] Threshold for determining labelling Channel X
[thresholdSigG_X] Threshold for what gets used in scoring of Channel X
'''
import numpy as np
class storageClass:
    theDict = {}
    def __init__(self,tempShape):
        self.data = np.zeros(tempShape,dtype='uint8')
    def add(self,nameIn,dataIn):
        lenDict = len(self.theDict)
        if lenDict<8:
            self.theDict.update({nameIn:lenDict})
            for z in range(self.data.shape[2]):
                self.data[:,:,z]+=(dataIn[:,:,z].astype(np.uint8)*np.power(2,lenDict).astype(np.uint8))
    def get(self,nameIn):
        return (self.data/np.power(2,self.theDict[nameIn]))%2