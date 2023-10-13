'''
Created on 1 Dec 2016

@author: s1144899

To be run once as takes a while:

'''
import numpy as np,nrrd
from scipy import ndimage
'''
theMask = nrrd.read("/media/s1144899/JaneliaBlue/Potential New Templates/CQr/Templates/tempBrainMask.nrrd")[0]
theMask = theMask>0
distanceChart = np.zeros(theMask.shape,dtype=np.int16)
distanceChart+=theMask
theMask = distanceChart>0
i=0
struct = ndimage.morphology.generate_binary_structure(3,1)
while (np.min(theMask)==0):
    print i
    theMask = ndimage.morphology.binary_dilation(theMask,structure=struct)
    distanceChart+=theMask
    i+=1
nrrd.write("/media/s1144899/JaneliaBlue/Potential New Templates/CQr/MaskSpreadBrain.nrrd",distanceChart)
'''
'''

Later usage might require:

distanceChart = np.max(distanceChart)-distanceChart

distanceChart = nrrd.read("/media/s1144899/JaneliaBlue/Potential New Templates/CQr/MaskSpreadVNC.nrrd")[0]
distanceChart = np.max(distanceChart)-distanceChart
nrrd.write("/media/s1144899/JaneliaBlue/Potential New Templates/CQr/MaskSpreadVNCInverse.nrrd",distanceChart.astype(np.int16))
'''

distanceChart = nrrd.read("/media/s1144899/JaneliaBlue/Potential New Templates/CQr/MaskSpreadBrain.nrrd")[0]
distanceChart = np.max(distanceChart)-distanceChart
nrrd.write("/media/s1144899/JaneliaBlue/Potential New Templates/CQr/MaskSpreadBrainInverse.nrrd",distanceChart.astype(np.int16))

'''
'''