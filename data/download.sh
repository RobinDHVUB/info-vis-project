#!/bin/bash

if [ ! -d ./data ]; then
    mkdir data
fi
if [ ! -d ./data/raw ]; then
    mkdir data/raw
fi

# Download subject data
for subject in 001 002 003 004 005 006 007 008 009 010 011 012 013 014 015 016 017 018 019
do 
    if [ ! -d data/raw/sub${subject} ]; then
        mkdir data/raw/sub${subject}
        if [ "$subject" == 019 ]; then
            wget -c "http://openfmri.s3.amazonaws.com/tarballs/ds117_R0.1.1_sub${subject}_raw.tgz" -O- | tar -C $PWD/data/raw/sub${subject} -xvzf - sub${subject}/MEG/*sss.fif
            mv data/raw/sub${subject}/sub${subject}/MEG/* data/raw/sub${subject}
            rm -rf data/raw/sub${subject}/sub${subject}
        else 
            wget -c "http://openfmri.s3.amazonaws.com/tarballs/ds117_R0.1.1_sub${subject}_raw.tgz" -O- | tar -C $PWD/data/raw/sub${subject} -xvzf - ds117/sub${subject}/MEG/*sss.fif
            mv data/raw/sub${subject}/ds117/sub${subject}/MEG/* data/raw/sub${subject}
            rm -rf data/raw/sub${subject}/ds117
        fi 
    fi
done