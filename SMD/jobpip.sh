#!/bin/bash

# Functions
mysbatch () {
    sbatch \
	--parsable \
	-N $Nodes \
	-n $Cores \
	-t $Time \
	--gres=gpu:$Gpus \
	-o slurm_${cmstr}.log \
	-p $Partition -q $Queue \
	-J ${cmstr} \
	$@
}
# Jobname Argument
if [ -z "$1" ]; then
    echo "Please enter a unique job name";read jobname
else
    jobname=$1
fi

# Set Defaults
Nodes=1
Cores=8
Gpus=1
Partition=asinghargpu1
Queue=asinghargpu1
Time=5-4:00
threads=$(expr $Cores - $Gpus)

# Start Job Control
mynamd="/scratch/jvant/namd-grid2.13/Linux-x86_64-g++"
systems=(open closed)


# Main
for sys in ${systems[@]}; do
    for i in {0..9}; do
	cd $sys/$i
	jobid=""
	cmstr=$jobname-$sys-replica$i
	# NAMD
	cat <<EOF > tmp-runnamd
#!/bin/bash
module load openmpi/3.0.3-gnu-7x-centos75 
$mynamd/namd2 +p${threads} twostatedensity.namd
EOF
	if [ -z $jobid ];then
	    jobid=$(mysbatch tmp-runnamd)
	else
	    jobid=$(mysbatch -d afterany:$jobid tmp-runnamd)
	fi
	echo "Job named " $cmstr ", submitted with JOBID: " $jobid
    done
    cd -
done
exit
