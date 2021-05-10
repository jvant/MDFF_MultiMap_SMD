#!/usr/bin/env bash

############################################################## 
# 
# Author:               John Vant 
# Email:              jvant@asu.edu 
# Affiliation:   ASU Biodesign Institute 
# Date Created:          200323
# 
############################################################## 
# 
# Usage: 
# 
############################################################## 
# 
# Notes: 
# 
############################################################## 

test -z ${1} && echo "Please enter the path to the traj file as an argument E.g. </path/to/traj/my.traj>"
test -z ${1} && exit

traj=${1}

echo "Analyzing $traj"

awk '{var = $4 - $15; print var, $2, $3, $4, $15}' $traj | grep -v mdff > tmp.dat

echo "python time!"
/bin/python <<EOF

import matplotlib as mpl
mpl.use('GTK')

import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt("tmp.dat",skiprows=11)
# print(data)
diff = [x[0] for x in data]
mdff0 = [x[1] for x in data]
mdff1 = [x[2] for x in data]
mdff = [x[3] for x in data]
x0 = [x[4] for x in data]

plt.plot(diff,label=diff)
plt.plot(mdff0,label=mdff0)
plt.plot(mdff1, label=mdff1)
plt.plot(mdff, label=mdff)
plt.plot(x0, label=x0)
# plt.legend()
plt.show()

exit()

EOF

rm tmp.dat

exit

