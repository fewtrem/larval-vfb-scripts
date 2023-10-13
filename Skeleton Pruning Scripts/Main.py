'''
Created on 8 Apr 2017

@author: s1144899
'''  
ID = '**ID**'
FLIP = '**F**'
FLIP_ = '**F_**'
CHAN = '**S**'

OUTID = '**OID**'
VNC = "**VNC**"
BRAIN = "**BRAIN**"
SKEL = "skel"
LABEL = "label"
REF = "ref"
# based on notebook "Skel1000 - 1 Prune the training set"

import os,nrrd,numpy as np,sys,pickle
# /afs/inf.ed.ac.uk/user/s11/s1144899/PhD/Python Projects/AlignNet2/Local/Condenser/Scripts/pruneSkeleton
# (imported in below:)
from pruneInterface import pruneSkeleton
# /afs/inf.ed.ac.uk/user/s11/s1144899/PhD/Python Projects/ml2017/ipythonResultsCBNonCB
from CBNonCB.finalModelSetUp import getAModel
# read the settings file:
settingsPath = sys.argv[1]
fI = open(settingsPath)
settings = pickle.load(fI)
fI.close()

outFolderPath = settings['outFolderPath']
imgFilesPaths = settings['imgFilesPaths']

thisIDListPath = sys.argv[2]
outID = os.path.basename(thisIDListPath).replace(".pkl","")
fI = open(thisIDListPath)
idList = pickle.load(fI)
fI.close()

# load in the tensorflow model:
cnnModel = getAModel(settings['modelA'])

# Do the pre stuff - with the templates:
distanceCharts = {}
for thisType in settings['distanceChartFilePaths']:
    distanceCharts[thisType] = nrrd.read(settings['distanceChartFilePaths'][thisType])[0]

print "Running through list"
for i in range(len(idList)):
    thisID=idList[i]
    print outID,"---",thisID,"---"
    thisOutFolderPath =outFolderPath.replace(ID,thisID)
    if not os.path.isdir(thisOutFolderPath):
        os.mkdir(thisOutFolderPath)
    for thisFlip in ['','F']:
        thisFlip_ = thisFlip
        if thisFlip=='F':
            thisFlip_ = '_F'
        for thisChan in ['R','G']:
            try:
            #if True:
                #check file locs:
                toOpen = {}
                for thisPathID in imgFilesPaths:
                    thisPath = imgFilesPaths[thisPathID].replace(ID,thisID).replace(FLIP,thisFlip).replace(CHAN,thisChan)
                    if os.path.isfile(thisPath):
                        toOpen[thisPathID]=thisPath
                # if OK then open them:
                if len(toOpen)==len(imgFilesPaths):
                    imgData = {}
                    for thisPathID in toOpen:
                        imgData[thisPathID] = nrrd.read(toOpen[thisPathID])[0]
                    thisType = VNC
                    if imgData[REF].shape[0]>imgData[REF].shape[1]:
                        thisType = BRAIN 
                    # now process them:
                    thisOutFileName = settings['outFileName'].replace(ID,thisID).replace(FLIP,thisFlip).replace(CHAN,thisChan)
                    thisOutFilePath = os.path.join(thisOutFolderPath,thisOutFileName)
                    pruneSkeleton(settings,imgData[SKEL],imgData[LABEL],imgData[REF],distanceCharts[thisType],cnnModel,thisOutFilePath)

            except:
                print outID,":","Error"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
    fO = open(os.path.join(thisOutFolderPath,settings['settingsSaveName']),'w')
    pickle.dump(settings,fO)
    fO.close()
    i+=1
