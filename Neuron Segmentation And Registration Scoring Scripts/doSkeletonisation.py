'''
Created on 30 Oct 2016

@author: s1144899

Run the FIJI skeletonisation tool!
'''
import  nrrd2, numpy as np, nrrd, subprocess,datetime

fijiMacro = "open(\"**REPLACE**\");\n\
run(\"Skeletonize (2D/3D)\");\n\
run(\"Nrrd ... \", \"nrrd=[**REPLACE**]\");"
def doSkeletonisation(settings,savedis):
    print "Pipeline: Making Skeletons For Each Neuron..."
    aF = datetime.datetime.now()
    # we will open all channels and get the thresholded images:
    for thisFileGet in settings['vfileInNamesRG']:
        print "Pipeline:   Channel: ",thisFileGet[0]
        if savedis['set'] == True:
            labeledImg = savedis["LI_"+thisFileGet[0]] # labeledImg NOT MASKED YET!
            #nomIds = savedis["NID_"+thisFileGet[0]]
        else:
            # load this version of the labelled image for identifying neurons:
            labeledImg = nrrd2.read(settings['vlabelsNamePre']+thisFileGet[0]+".nrrd")[0]
            #nomIds = np.max(labeledImg)+1
        thisNRRDOut = (labeledImg>0).astype(np.uint8)
        nrrdPath = settings['skelFileNamePre']+thisFileGet[0]+".nrrd"
        nrrd.write(nrrdPath,thisNRRDOut)
        # Edit the macro:
        toWrite = fijiMacro.replace("**REPLACE**",nrrdPath)
        f = open(settings['fijiMacroPath'],'w')
        f.write(toWrite)
        f.close()
        CodeForStart = "\""+settings['fijiPath']+"\" --headless --allow-multiple -macro \""+settings['fijiMacroPath']+"\"" 
        subprocess.call(CodeForStart,shell=True)
        # load in the skeletonised image:
        reSkelled = nrrd.read(nrrdPath)[0]>0
        nrrd.write(nrrdPath,reSkelled.astype(np.uint8))
    bF = datetime.datetime.now()
    print "Pipeline: Done Skeletonisation, Runtime:",(bF-aF)," seconds"
