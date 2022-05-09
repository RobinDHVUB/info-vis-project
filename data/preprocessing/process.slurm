#!/bin/bash
#SBATCH --job-name=preproc
#SBATCH --time=6:00:00
#SBATCH --ntasks=10
#SBATCH --cpus-per-task=4

module load Python/3.9.6-GCCcore-11.2.0
module load parallel/20210722-GCCcore-11.2.0

# Cwd
cd ~/info-vis-project

# Create processed folder
if [ ! -d /scratch/brussel/102/vsc10248/data ]; then
    mkdir /scratch/brussel/102/vsc10248/data
fi
if [ ! -d /scratch/brussel/102/vsc10248/data/processed ]; then
    mkdir /scratch/brussel/102/vsc10248/data/processed
else
    echo "processed folder exists, clear first"
    exit 0
fi

# Queue the preprocessing tasks
parallel --delay 0.2 -j $SLURM_NTASKS --joblog runtask.log --resume srun -N1 -n1 -c4 python data/preprocessing/process.py {} ::: {1..16}
wait

# Extract MEG coords and names
#python data/preprocessing/extract_metadata.py

# Archive
#tar -Jcvf /scratch/brussel/102/vsc10248/data/processed.tar.xz -C /scratch/brussel/102/vsc10248/data processed 