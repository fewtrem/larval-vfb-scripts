#include <stdio.h>
#include <stdint.h>
/*
 * based on (python):
def getUniquesLowMemory(inputData,counts):
    output = np.zeros(counts,dtype=np.int32)
    raveledInput = inputData.ravel()
    for i in range(len(raveledInput)):
        output[raveledInput[i]]+=1
    return counts
 *
 */
int uniqueVals(const int32_t * inputArrP, const long arrayLength, int32_t * outDataP) {
    int32_t * inputArr = (int32_t *) inputArrP;
    int32_t * outData = (int32_t *) outDataP;
	int i;

	for (i=0;i<arrayLength;i++){
		outData[inputArr[i]] +=1;
	}
	return 0;


}


