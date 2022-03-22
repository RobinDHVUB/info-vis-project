#!/bin/bash

# Make directory for raws
if [ ! -d data/raw ]; then
    mkdir data/raw
fi

# Download subject data
if ! test -f data/raw/sub-1-4.zip; then
    wget -P data/raw/sub-1-4.zip "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_sub01-04.zip"
    unzip data/raw/sub-1-4.zip
fi
#if ! test -f data/raw/sub-5-8.zip; then
#    wget -P data/raw/sub-5-8.zip "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_sub05-08.zip"
#    unzip data/raw/sub-5-8.zip
#fi
#if ! test -f data/raw/sub-9-12.zip; then
#    wget -P data/raw/sub-9-12.zip "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_sub09-12.zip"
#    unzip data/raw/sub-9-12.zip
#fi
#if ! test -f data/raw/sub-13-16.zip; then
#    wget -P data/raw/sub-13-16.zip "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_sub13-16.zip"
#    unzip data/raw/sub-13-16.zip
#fi

# Download metadata
if ! test -f data/raw/metadata.zip; then
    wget -P data/raw/metadata.zip "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_metadata.zip"
    unzip data/raw/metadata.zip
fi

# Download stimuli
if ! test -f data/raw/stimuli.zip; then
    wget -P data/raw/stimuli.zip "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_stimuli.zip"
    unzip data/raw/stimuli.zip
fi