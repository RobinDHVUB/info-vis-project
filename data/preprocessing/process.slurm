#!/bin/bash
#SBATCH --job-name=preproc
#SBATCH --time=6:00:00
#SBATCH --ntasks=19
#SBATCH --cpus-per-task=4

module load Python/3.9.6-GCCcore-11.2.0
module load parallel/20210722-GCCcore-11.2.0

# Cwd
cd ~/info-vis-project

# Create processed folder
if [ ! -d /data/brussel/102/vsc10248/data ]; then
    mkdir /data/brussel/102/vsc10248/data
fi
if [ ! -d /data/brussel/102/vsc10248/data/processed ]; then
    mkdir /data/brussel/102/vsc10248/data/processed
else
    echo "processed folder exists, clear first"
    exit 0
fi

# Queue the preprocessing tasks                                                                                              # v directory where data/raw is 
parallel --delay 0.2 -j $SLURM_NTASKS --joblog runtask.log --resume srun -N1 -n1 -c4 python data/preprocessing/process.py {} /scratch/brussel/102/vsc10248 /data/brussel/102/vsc10248 ::: $(ls -1 /scratch/brussel/102/vsc10248/data/raw)
wait                                                                                                                                                       # ^ directory where data/processed will be                                                                                                                                    

# Extract MEG coords and names
python data/preprocessing/extract_meg_coords.py

# Archive
tar -Jcvf /data/brussel/102/vsc10248/data/processed.tar.xz -C /data/brussel/102/vsc10248/data processed 