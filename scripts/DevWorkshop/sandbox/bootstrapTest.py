import numpy as np;
from medinfo.common.Util import ProgressDots;

def calcStat(data):
	rate = float(sum(data)) / len(data);
	return rate;


def main(nResamples = 1000, sampleSize = 200, positiveCount = 180):
	

	
	
	confidenceInterval = 0.95

	sample = list()
	for i in range(sampleSize):
		value = 0;
		if i < positiveCount:
			value = 1;
		sample.append(value);
	sample = np.array(sample);

	print("Sample Rate: ",calcStat(sample) );

	rng = np.random.RandomState(nResamples);	# Seed with number for consistency
	bootstrapValues = list();

	prog = ProgressDots();
	for i in range(nResamples):
		indices = rng.random_integers(0, sampleSize-1, sampleSize);	# Get indices of resample items (with replacement)
		resample = sample[indices];
		bootstrapValues.append( calcStat(resample) );
		prog.update();

	ciFractionLow = (1.0-confidenceInterval) / 2;
	ciFractionHigh= confidenceInterval + ciFractionLow;

	bootstrapValues.sort();
	print("Sample Rate 95%CI Low", bootstrapValues[int(ciFractionLow*nResamples)] )
	print("Sample Rate 95%CI High", bootstrapValues[int(ciFractionHigh*nResamples)] )

if __name__ == "__main__":
	main();
