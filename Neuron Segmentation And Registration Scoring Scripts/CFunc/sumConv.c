#include <stdio.h>
#include <math.h>
#include <stdint.h>

/* PYTHON function this is based on:
 * for ex in range(-exploreB[0],exploreB[0]+1):
                for ey in range(-exploreB[1],exploreB[1]+1):
                    for ez in range(-exploreB[2],exploreB[2]+1):
                        #nothing
                        thisFloat = convFloatStore[x+ex,y+ey,z+ez]
                        # 3 operations....
                        meanDelta = thisFloat[0]*thisFloat[1]-thisTemp[0]*thisTemp[1]
                        output=thisTemp[2]+\
                        thisFloat[2]+\
                        meanDelta*meanDelta*borderProd+\
                        -2*thisFloat[1]*thisTemp[1]*storageArray[x,y,z,ex+exploreB[0],ey+exploreB[1],ez+exploreB[2]]+\
                        2*thisTemp[3]*meanDelta+\
                        -2*thisFloat[3]*meanDelta
                        storageArray[x,y,z,ex+exploreB[0],ey+exploreB[1],ez+exploreB[2]] = output
 */
void sumConv(const int32_t * diffArrP, const long * dimsImP, const long * exploresP, const double * tempStoreP,const double * floatStoreP, const int tTPx, const int tTPy, const int tTPz, const int convMax, double * outs){
	int dimsIm[3];
	int explores[3];
	int ex,ey,ez,j;
	double meanT,sdDivisorT,sumsqT,sumT,meanF,sdDivisorF,sumsqF,sumF,meanDelta,result;
	int thisFloatPos,thisTempPos,eVal;
    for (j=0;j<3;j++){
    	dimsIm[j] = (int)dimsImP[j];
    	explores[j] = (int)exploresP[j];
    }
	int exploreDims[3] = {explores[0]*2+1,explores[1]*2+1,explores[2]*2+1};
    int exploresMax = exploreDims[2]*exploreDims[1]*exploreDims[0];
	thisTempPos = tTPz+(tTPy+(tTPx)*dimsIm[1])*dimsIm[2];
	meanT = tempStoreP[thisTempPos*4];
	sdDivisorT = tempStoreP[thisTempPos*4+1];
	sumsqT = tempStoreP[thisTempPos*4+2];
	sumT = tempStoreP[thisTempPos*4+3];
    for(ex=-explores[0];ex<explores[0]+1;ex++){
        for(ey=-explores[1];ey<explores[1]+1;ey++){
            for(ez=-explores[2];ez<explores[2]+1;ez++){
            	thisFloatPos = tTPz+ez+(tTPy+ey+(tTPx+ex)*dimsIm[1])*dimsIm[2];
            	meanF = floatStoreP[thisFloatPos*4];
            	sdDivisorF = floatStoreP[thisFloatPos*4+1];
            	sumsqF = floatStoreP[thisFloatPos*4+2];
            	sumF = floatStoreP[thisFloatPos*4+3];
            	meanDelta = meanF-meanT;
            	eVal = ez+explores[2]+(ey+explores[1]+(ex+explores[0])*exploreDims[1])*exploreDims[2];
            	result = sumsqT+sumsqF+meanDelta*meanDelta*(double)convMax+2*((sumT-sumF)*meanDelta-sdDivisorF*sdDivisorT*(double)diffArrP[thisTempPos*exploresMax+eVal]);
            	//outs[thisTempPos*exploresMax+eVal] = result;
            	outs[eVal] = result;
            }	
        }
    }
}
