'''
Created on 7 Dec 2015

@author: s1144899
'''
import pickle, nrrd2, numpy as np
from getNeuronScores import getNeuronScores
'''
settings - the settings...
storage - the storage object.
'''
def doNeuronScoring(settings,storage,hRF,savedis):
    print "Pipeline: Calculating Scores For Each Neuron..."
    # we will open all channels and get the scores....
    scoresSAVE = {}
    for thisFileGet in settings['vfileInNamesRG']:
        print "Pipeline:   Channel: ",thisFileGet[0]
        if savedis['set'] == True:
            labeledImg = savedis["LI_"+thisFileGet[0]] # labeledImg NOT MASKED YET!
            nomIds = savedis["NID_"+thisFileGet[0]]
        else:
            # load this version of the labelled image for identifying neurons:
            labeledImg = nrrd2.read(settings['vlabelsNamePre']+thisFileGet[0]+".nrrd")[0]
            nomIds = np.max(labeledImg)+1
        # get the score values:
        newScores = getNeuronScores(settings,labeledImg,nomIds,hRF,storage,thisFileGet[0])
        scoresSAVE[thisFileGet[0]] = newScores
    # save a scoresR file
    if settings['vsaveScores'] == True:
        savePath = settings['vscoreFilePre']+".pkl"
        f = open(savePath,'w')
        pickle.dump(scoresSAVE, f)
        f.close()
    print "Pipeline: Done Calculating Scores For Each Neuron..."
    return
    # get the final score for each neuron (write it out with CoM):
