#!/usr/bin/env tcl

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

mol default style NewCartoon
foreach state {"closed" "open"} {
    foreach res { 1 3 5 7 9 11 } {

	mol new ./${state}/${res}/adk.psf
	mol addfile ./${state}/${res}/2statedensity.dcd waitfor -1
	mol addfile ./${state}/${res}/finish.dx
	mol rename top ${state}_${res}
    }
}

