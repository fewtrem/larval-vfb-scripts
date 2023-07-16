import numpy as np, nrrd, datetime, pickle
from storage import storageClass
from thresholdNeurons import thresholdNeuronsForScoring, thresholdNeuronsForLabelling
from doSegmentation import doNeuronSegmentation, makeCombinedROI
from wholeBrainRepeats import getField, exportFieldNRRD
from doSkeletonisation import doSkeletonisation

def runScript(theSettings):
    print "Pipeline: Loading Mask..."
    a = datetime.datetime.now()
    # Set the mask and template file on the type that we found earlier:
    if 'thisType' not in theSettings:
        theSettings['thisType'] = "VNC"
        checkShape = nrrd.read(theSettings['typeCheckFileLoc'])[0].shape
        if checkShape[0]>checkShape[1]:
            theSettings['thisType'] = "Brain"
    if theSettings['thisType']=="VNC":
        maskFile=theSettings['maskFileVNC']
        vTempLocFile = theSettings['vTempVNCLoc']
    elif theSettings['thisType']=="Brain":
        maskFile=theSettings['maskFileBrain']
        vTempLocFile = theSettings['vTempBrainLoc']
    # Load the template (here so we can get shape):
    tempImageStack = nrrd.read(vTempLocFile)[0]
    theSettings['tempShape'] = tempImageStack.shape
    # Create the storage np array (now object) to SAVE space!
    stoarageInstance = storageClass(theSettings['tempShape'])
    
    # get mask if required (note need this IF statement again later if we refer to using a mask!
    if theSettings['useMask']==True:
        maskImageStack = nrrd.read(maskFile)[0]
        # Ensure boolean:
        maskImageStack[maskImageStack>0]=1
        # plop it in the storage array:
        stoarageInstance.add('mask',maskImageStack)
        maskImageStack = None
    else:
        stoarageInstance.add('mask',np.ones(stoarageInstance.data.shape,dtype=np.uint8))
    # Should still be just 1x uint8 arrays of approx. 300MB 
    #print  "Alignopolis: Using ",(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000),"MB"
    print "Pipeline: Loading Float..."
    floatImageStack = nrrd.read(theSettings['inputReformatBG'])[0].astype('uint8')
    # The idea is that we now do the segmentation and determine where the neurons are we want to keep:
    neuronSegments = {}
    if theSettings['doSegmentation']==True:
        # Get the new scoring labels:
        thresholdNeuronsForScoring(theSettings,stoarageInstance)
        # Threshold out the neurons using pipes etc. (will update stoarageInstance) and remove small stuff:
        thresholdNeuronsForLabelling(theSettings,stoarageInstance)
        # do the neuron segmentation and save as images:
        neuronSegments = doNeuronSegmentation(theSettings,stoarageInstance)
    if 'set' not in neuronSegments:
        neuronSegments['set']=True
        for thisFileGet in theSettings['vfileInNamesRG']:
            neuronSegments["LI_"+thisFileGet[0]] = nrrd.read(theSettings['vlabelsNamePre']+thisFileGet[0]+".nrrd")[0]
            neuronSegments["NID_"+thisFileGet[0]] = np.max(neuronSegments["LI_"+thisFileGet[0]])+1
            stoarageInstance.add('thresholdSigLab_'+thisFileGet[0],neuronSegments["LI_"+thisFileGet[0]]>0)
    scoreField = -np.ones((1,1))
    # Now we go and get scores for the stacks where the neuron signal is:
    if theSettings['doScoring']==True:
        # We also want to actually score the image but a different ROi for that is required:
        if theSettings['getSpecificROI'] == True:
            # get the total ROI:
            ROIToAdd = makeCombinedROI(theSettings,stoarageInstance)
        else:
            ROIToAdd = np.ones((10))
                scoreFromTemp = True
                if 'scoreFromTemp' in theSettings:
                    if theSettings['scoreFromTemp']==False:
                        scoreFromTemp = False
                if scoreFromTemp == False:
                    print "scoring from Temp->Float i.e. in float space where is best temp pos."                
                    scoreField = getField(theSettings['score'],floatImageStack,tempImageStack,ROIToAdd)
                else:
                    print "scoring from Float->Temp i.e. in template space where is best float pos."
                    scoreField = getField(theSettings['score'],tempImageStack,floatImageStack,ROIToAdd)
        # clear some memory!
        del ROIToAdd
        del tempImageStack
        del floatImageStack          
        # note that this sets anything outside the stoarageInstance.get('thresholdG_'+thisFileGet[0]) to zero!
        exportFieldNRRD(theSettings,stoarageInstance,scoreField)
    else:
        neuronSegments = {'set':False}
    # NEURON scoring:
    if theSettings['doScoring']==True:
        # Neural scoring:
        doNeuronScoring(theSettings,stoarageInstance,scoreField,neuronSegments)
    del scoreField
    # Do the skeletonisation too:
    if theSettings['doSkeletonisation']==True:
        # add the skeletonisation function
        doSkeletonisation(theSettings,neuronSegments)
    b = datetime.datetime.now()
    print "Pipeline: Total time taken in program:",str((b-a))," seconds"
