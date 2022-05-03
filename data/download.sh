#!/bin/bash

if [ ! -d ./data ]; then
    mkdir data
fi
if [ ! -d ./data/raw ]; then
    mkdir data/raw
fi

# Download subject data according to underneath naming from dataset description:

# Version 0.1.1:
# openfmri#     original# 
# sub001        subject_01 --> gone in v1
# sub002        subject_02
# sub003        subject_03
# sub004        subject_05
# sub005        subject_06 --> gone in v1
# sub006        subject_08
# sub007        subject_09
# sub008        subject_10
# sub009        subject_11
# sub010        subject_12
# sub011        subject_14 --> 04 in v1
# sub012        subject_15 
# sub013        subject_16
# sub014        subject_17
# sub015        subject_18
# sub016        subject_19 --> gone in v1
# sub017        subject_23
# sub018        subject_24
# sub019        subject_25

# Version 1.0.0:
# Please note that the subject ordering has changed since version 0.1.x (non-BIDS) of this 
# dataset. Additionally, three subjects have been left out. The mapping is as follows:
# 0.1.x:   02 03 05 14 08 09 10 11 12 15 16 17 18 23 24 25
# current: 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16

# Downloading using openfmri naming
for subject in 002 003 004 006 007 008 009 010 011 012 013 014 015 017 018 019
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

# Renaming to v1.0.0 naming
mv data/raw/sub002/ data/raw/sub001
mv data/raw/sub003/ data/raw/sub002
mv data/raw/sub004/ data/raw/sub003
mv data/raw/sub006/ data/raw/sub005
mv data/raw/sub007/ data/raw/sub006
mv data/raw/sub008/ data/raw/sub007
mv data/raw/sub009/ data/raw/sub008
mv data/raw/sub010/ data/raw/sub009
mv data/raw/sub011/ data/raw/sub005
mv data/raw/sub012/ data/raw/sub010
mv data/raw/sub013/ data/raw/sub011
mv data/raw/sub014/ data/raw/sub012
mv data/raw/sub015/ data/raw/sub013
mv data/raw/sub017/ data/raw/sub014
mv data/raw/sub018/ data/raw/sub015
mv data/raw/sub019/ data/raw/sub016

# Download metadata
wget "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_metadata.zip"
unzip ds000117_R1.0.0_metadata.zip
mv ds000117_R1.0.0_metadata/participants.tsv data/raw
rm -rf ds000117_R1.0.0_metadata*