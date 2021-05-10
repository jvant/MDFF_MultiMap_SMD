import os
import glob
def mymkdir(s):
	if not os.path.exists(s):
		os.makedirs(s)
def mysymlink(source, dest):
	if not os.path.exists(dest):
		os.symlink(source, dest)

# Set parameters here
molname="adk"

script = '''set molname adk
set temperature 300.0
set logfreq 500
set dcdfreq 2500
#restarts cost almost nothing for small systems
set restartfreq 25000

# Input
structure   $molname.psf
coordinates $molname.pdb

paraTypeCharmm          on
parameters charmm/par_all36m_prot.prm

#Force field modifications
exclude scaled1-4
1-4scaling 1.0
dielectric 1.0
gbis                on
switching           on
VDWForceSwitching   on
alphacutoff         14.
switchdist          15.
cutoff              16.
pairlistdist        17.
ionconcentration    0.1
solventDielectric   80.0
sasa                on
stepspercycle       20
margin              2.0
rigidBonds          ALL
timestep            2.0

#Thermostat. I always use a damping coefficient of 1, but that might be my membrane bias.
langevin on
temperature $temperature
langevinTemp $temperature
langevinDamping 1.0
langevinHydrogen no

#Extra restraints
extraBonds yes
foreach fil [list $molname-chirality.txt $molname-cispeptide.txt $molname-ssrestraints.txt] {
	extraBondsFile $fil
}

# Standard output frequencies
outputEnergies          $logfreq
outputTiming            $logfreq
DCDFreq $dcdfreq
restartfreq $restartfreq

#Set outputname, GRIDFILE, and which colvar to operate with.
%s

minimize 500
#Lookup what the current colvar value is.
run 0
cv update
%s
cv config "
harmonic {
    name smd
    colvars $cvname
    centers $initvalue
    targetCenters $finalvalue
    forceConstant $forceconstant
    targetNumSteps 10000000
    outputAccumulatedWork on
    outputCenters on
}
"

reinitvels $temperature
run 10000000 ;# 20ns

'''


def createdirectory(start, finish, resolution):
	mymkdir(start)
	os.chdir(start)
	mymkdir(str(resolution))
	os.chdir(str(resolution))
	for fname in ["%s.psf" % molname, "%s-chirality.txt" % molname, "%s-cispeptide.txt" % molname, "%s-ssrestraints.txt" % molname]:
		mysymlink("../../../build/%s" % fname, fname)
	mysymlink("../../../build/%s.pdb" % start, "%s.pdb" % molname)
	mysymlink("../../../build/%s-%d.dx" % (start, resolution), "start.dx")
	mysymlink("../../../build/%s-%d.dx" % (finish, resolution), "finish.dx")
	mysymlink("../../../build/%s-%d-grid.dx" % (start, resolution), "start-grid.dx")
	mysymlink("../../../build/%s-%d-grid.dx" % (finish, resolution), "finish-grid.dx")
	mysymlink("../../twostatedensity.conf", "twostatedensity.conf")
	mysymlink("../../onestatepotential.conf", "onestatepotential.conf")
	mysymlink("../../../charmm", "charmm")
        mysymlink("../../../build/com.dat", "com.dat")        
        if resolution < 5:
                mysymlink("../../../build/gridpdb-noh.pdb", "gridpdb.pdb")
        else:
                mysymlink("../../../build/gridpdb-bb.pdb", "gridpdb.pdb")

	twostatedensity = script % ('''
outputname 2statedensity
set GRIDFILE [list start.dx finish.dx]
mgridForce               on
for {set i 0} {$i < [llength $GRIDFILE]} {incr i} {
    mgridForceFile $i      gridpdb.pdb
    mgridForceCol $i       O
    mgridForceChargeCol $i B
    mgridForcePotFile $i   [lindex $GRIDFILE $i]
    mgridForceScale $i     0 0 0
}
colvars on
source twostatedensity.conf
''',
'''
set cvname mdff
set initvalue [cv colvar $cvname value]
set finalvalue [expr { -1 * $initvalue }]
set forceconstant [expr { 1.0 / (2 * abs($initvalue))}]

'''
)
	onestatepotential = script % ('''
outputname 1statepotential
set GRIDFILE [list start-grid.dx finish-grid.dx]
mgridForce               on
for {set i 0} {$i < [llength $GRIDFILE]} {incr i} {
    mgridForceFile $i      gridpdb.pdb
    mgridForceCol $i       O
    mgridForceChargeCol $i B
    mgridForcePotFile $i   [lindex $GRIDFILE $i]
    mgridForceScale $i     0 0 0
}
colvars on
source onestatepotential.conf
''',
'''
set cvname mdfffinish
set initvalue [cv colvar $cvname value]
set finalvalue 0
set forceconstant [expr { 10.0 / (abs($initvalue))}]
''')
        namdfiles = ["twostatedensity", "onestatepotential"]
	for i, namdscript in enumerate([twostatedensity, onestatepotential]):
		fout = open("%s.namd" % namdfiles[i], "w")
		fout.write(namdscript)
		fout.close()
	os.chdir("../..")

for start, finish in zip(['open', 'closed'], ['closed', 'open']):
	for resolution in [1,3,5,7,9,11]:
		createdirectory(start, finish, resolution)
