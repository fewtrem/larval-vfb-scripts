'''
Created on 20 Feb 2017

@author: s1144899
'''
import nrrd,numpy as np
from scipy import ndimage
maskSpread = nrrd.read("/media/s1144899/JaneliaBlue/Potential New Templates/CQr/MaskSpreadBrainInverse.nrrd")[0]
theMaskTot = np.zeros(maskSpread.shape,dtype=np.int16)
struct = ndimage.morphology.generate_binary_structure(3,1)
curBin = maskSpread==0
i=0
while (np.max(curBin)==1):
    print i
    curBin = ndimage.morphology.binary_erosion(curBin,structure=struct)
    theMaskTot+=curBin
    i+=1
maskSpread2 = maskSpread-theMaskTot
nrrd.write("/media/s1144899/JaneliaBlue/Potential New Templates/CQr/MaskSpreadBrainInverse2.nrrd",maskSpread2)