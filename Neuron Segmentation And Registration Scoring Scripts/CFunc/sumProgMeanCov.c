#include <stdio.h>
#include <stdint.h>
/*
 * based on (python):
  for z in range(convB[2],bT.shape[2]-convB[2]):
    tempSumX = np.sum(bT[:,:,z-convB[2]:z+convB[2]+1],axis=2)
    for y in range(convB[1],bT.shape[1]-convB[1]):
        tempSumY = np.sum(tempSumX[:,y-convB[1]:y+convB[1]+1],axis=1)
        endA = convB[0]*2
        outputA = np.sum(tempSumY[0:endA+1])
        bT2[-1,y,z] = outputA
        for x in range(0,bT.shape[0]-convB[0]*2-1):
            endA+=1
            outputA = outputA-tempSumY[x]+tempSumY[endA]
            bT2[x,y,z] = outputA
 *
 *We need a store of some results, namely the MEAN and SDEV of the surroundings for each cell and we also need the sums of the squares of the internals.
 *We We are returning squares, so the maximum value is: (255^2*11*11*3)  So we need 16 bits in the output, or a float of kinds.
 *
 */
int sumProg(const unsigned short * diffArrP, const long * dimsImP, long * convWidthsP, int32_t * outDataP) {
	int convWidths[3];
	int dimsIm[3];
	int j;
    for (j=0;j<3;j++){
    	dimsIm[j] = (int)dimsImP[j];
    	convWidths[j]=(int)convWidthsP[j];
    }
    unsigned short * diffArr = (unsigned short *) diffArrP;
    int32_t * outData = (int32_t *) outDataP;
	int x,y,z;
	int a,b;
	int tHelpers[3] = {1,dimsIm[0],dimsIm[1]*dimsIm[0]};
	long tempSumX[tHelpers[2]];
	long tempSumY[tHelpers[1]];
	long thisSum;
	int endA;

	for (z=convWidths[2];z<dimsIm[2]-convWidths[2];z++){
		for(a=0;a<tHelpers[2];a++){
			thisSum = 0;
			for(b=-convWidths[2];b<convWidths[2]+1;b++){
				thisSum+=(long)diffArr[z+b+a*dimsIm[2]];
			}
			tempSumX[a]=thisSum;
		}
		for (y=convWidths[1];y<dimsIm[1]-convWidths[1];y++){
			for(a=0;a<tHelpers[1];a++){
				thisSum = 0;
				for(b=-convWidths[1];b<convWidths[1]+1;b++){
					thisSum+=tempSumX[y+b+a*dimsIm[1]];
				}
				tempSumY[a]=thisSum;
			}
			thisSum = 0;
			for(endA=0;endA<convWidths[0]*2+1;endA++){
				thisSum+=tempSumY[endA];
			}
			for (x=0;x<dimsIm[0]-convWidths[0]*2-1;x++){
				outData[(x+convWidths[0])*dimsIm[2]*dimsIm[1]+y*dimsIm[2]+z] = (int32_t)thisSum;
				thisSum = thisSum-tempSumY[x]+tempSumY[endA];
				endA+=1;
			}
			outData[(x+convWidths[0])*dimsIm[2]*dimsIm[1]+y*dimsIm[2]+z]= thisSum;
		}

	}
	return 0;


}


