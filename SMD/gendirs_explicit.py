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
structure   ${molname}_solv-ion.psf
coordinates ${molname}_solv-ion.pdb

paraTypeCharmm          on
#parameters charmm/par_all36m_prot.prm
#parameters charmm/par_all36_carb.prm 
#parameters charmm/par_all36_lipid.prm
#parameters charmm/par_all36_cgenff.prm
#parameters charmm/toppar_water_ions_namd.str

parameters          charmm/par_all36m_prot.prm
parameters          charmm/par_all36_na.prm
parameters          charmm/par_all36_carb.prm
parameters          charmm/par_all36_lipid.prm
parameters          charmm/par_all36_cgenff.prm
parameters          charmm/toppar_water_ions_namd.str
parameters          charmm/toppar_dum_noble_gases.str
parameters          charmm/toppar_all36_prot_d_aminoacids.str
parameters          charmm/toppar_all36_prot_fluoro_alkanes.str
parameters          charmm/toppar_all36_prot_heme.str
parameters          charmm/toppar_all36_prot_na_combined.str
parameters          charmm/toppar_all36_prot_retinol.str
parameters          charmm/toppar_all36_na_nad_ppi.str
parameters          charmm/toppar_all36_na_rna_modified.str
parameters          charmm/toppar_all36_lipid_bacterial.str
parameters          charmm/toppar_all36_lipid_cardiolipin.str
parameters          charmm/toppar_all36_lipid_cholesterol.str
parameters          charmm/toppar_all36_lipid_inositol.str
parameters          charmm/toppar_all36_lipid_lps.str
parameters          charmm/toppar_all36_lipid_miscellaneous.str
parameters          charmm/toppar_all36_lipid_model.str
parameters          charmm/toppar_all36_lipid_prot.str
parameters          charmm/toppar_all36_lipid_pyrophosphate.str
parameters          charmm/toppar_all36_lipid_sphingo.str
parameters          charmm/toppar_all36_lipid_yeast.str
parameters          charmm/toppar_all36_lipid_hmmm.str
parameters          charmm/toppar_all36_lipid_detergent.str
parameters          charmm/toppar_all36_carb_glycolipid.str
parameters          charmm/toppar_all36_carb_glycopeptide.str
parameters          charmm/toppar_all36_carb_imlab.str


#Force field modifications
exclude scaled1-4
1-4scaling 1.0
dielectric 1.0
switching           on
VDWForceSwitching   on
# alphacutoff         14.
switchdist          10.
cutoff              12.
pairlistdist        16.
# ionconcentration    0.1
# solventDielectric   80.0
# sasa                on
stepspercycle       20
margin              2.0
rigidBonds          ALL
timestep            2.0


#Read PBC data into configuration file
#Slurp up the data file
set fp [open "./PBC_Values.str" r]
set file_data [read $fp]
close $fp

set data [split $file_data "
"]
set a [lindex $data 0 0]
set b [lindex $data 0 1]
set c [lindex $data 0 2]
set xcen [lindex $data 1 0]
set ycen [lindex $data 1 1]
set zcen [lindex $data 1 2]

cellBasisVector1     $a   0.0   0.0
cellBasisVector2    0.0    $b   0.0
cellBasisVector3    0.0   0.0    $c
cellOrigin          $xcen $ycen $zcen

wrapWater               on
wrapAll                 on
wrapNearest             off

# PME (for full-system periodic electrostatics)
PME                     yes;
PMEInterpOrder          6;
PMEGridSpacing          1.0;

# Pressure and volume control
useGroupPressure        yes
                           
useFlexibleCell         no
useConstantRatio        no


#Thermostat. I always use a damping coefficient of 1, but that might be my membrane bias.
langevin on
temperature $temperature
langevinTemp $temperature
langevinDamping 1.0
langevinHydrogen no

# constant pressure
langevinPiston          on
langevinPistonTarget    1.01325
langevinPistonPeriod    50.0
langevinPistonDecay     25.0
langevinPistonTemp      $temperature

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
	for fname in ["%s_solv-ion.psf", "%s_solv-ion.pdb", "%s-chirality.txt", "%s-cispeptide.txt", "%s-ssrestraints.txt"]:
		mysymlink("../../../build/%s" % fname % start, fname % molname)
	mysymlink("../../../build/%s-%d.dx" % (start, resolution), "start.dx")
	mysymlink("../../../build/%s-%d.dx" % (finish, resolution), "finish.dx")
	mysymlink("../../../build/%s-%d-grid.dx" % (start, resolution), "start-grid.dx")
	mysymlink("../../../build/%s-%d-grid.dx" % (finish, resolution), "finish-grid.dx")
	mysymlink("../../twostatedensity.conf", "twostatedensity.conf")
	mysymlink("../../onestatepotential.conf", "onestatepotential.conf")
	mysymlink("../../../charmm", "charmm")
        mysymlink("../../../build/com.dat", "com.dat")
        mysymlink("../../../build/PBC_Values.str", "PBC_Values.str")
        
        if resolution < 5:
                mysymlink("../../../build/%s_gridpdb-noh.pdb" % start, "gridpdb.pdb")
        else:
                mysymlink("../../../build/%s_gridpdb-bb.pdb"  % start, "gridpdb.pdb")

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
