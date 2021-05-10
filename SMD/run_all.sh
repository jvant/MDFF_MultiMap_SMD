#!/usr/bin/env bash

############################################################## 
# 
# Author:               John Vant 
# Email:              jvant@asu.edu 
# Affiliation:   ASU Biodesign Institute 
# Date Created:          200224
# 
############################################################## 
# 
# Usage: 
# 
############################################################## 
# 
# Notes: run all scripts
# 
############################################################## 
topdir=$(pwd)

if [ -z "$1" ]; then
    echo "Please enter a unique job name"
    read jobname
else
    jobname=$1
fi

for state in closed #open
do
#    for res in 1 3 5 7 9 11; # already launced res 5 as tests
    for res in 1 3 5 7 9 11
#    for res in 5; # Test
    do
	cd ${topdir}/${state}/${res}/
	${topdir}/submit twostatedensity.namd ${jobname}_${state}_${res}
	cd -
    done
done
