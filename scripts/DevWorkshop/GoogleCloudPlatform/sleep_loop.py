import time
import sys
t = int(sys.argv[1]) 
for i in range(0,t):
	while i < t:
		time.sleep(1)
		print('step', i + 1)
		break
