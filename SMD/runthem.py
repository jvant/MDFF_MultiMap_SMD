import subprocess
import os
for i in range(2):
	for resolution in [1,3,5,7,9,11]:
		for start in ['open', 'closed']:
			os.chdir("%s/%s" % (start, resolution))
			subprocess.call("~/Desktop/namd-globalgridobjects/Linux-x86_64-g++/namd2 +p8 test-%d.namd | tee test-%d.log " % (i,i), shell=True)
			os.chdir("../..")
