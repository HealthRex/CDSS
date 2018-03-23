# Stitch together patient ID files
# Muthu, April 2nd, 2016
# Manually feed it as arguments all the files you want to stitch following the name of the output file
# python MuthuDecayingWindows/StitchIDFiles.py outputfile input1 input2...

import sys

fileNames = sys.argv[2:]
with open (sys.argv[1], "w") as fout:
	for fname in fileNames:
		with open (fname) as fin:
			for line in fin:
				fout.write(line)
