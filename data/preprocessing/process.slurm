#!/bin/bash
#SBATCH --job-name=preproc
#SBATCH --time=6:00:00
#SBATCH --ntasks=19
#SBATCH --cpus-per-task=4

module load Python/3.9.5-GCCcore-10.3.0
module load parallel/20210622-GCCcore-10.3.0

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

# Queue the tasks
parallel --delay 0.2 -j $SLURM_NTASKS --joblog runtask.log --resume srun -N1 -n4 --exclusive python process.py {} ::: $(ls -1 /scratch/brussel/102/vsc10248/data/raw)
wait

# Archive
tar -Jcvf processed.tar.gz -C /data/brussel/102/vsc10248/data ./processed 