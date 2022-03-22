#!/bin/bash

# Make directory for raws
if [ ! -d data/raw ]; then
    mkdir data/raw
fi

# Download subject data
if ! test -f data/raw/ds000117_R1.0.0_sub01-04.zip; then
    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_sub01-04.zip"
    unzip data/raw/ds000117_R1.0.0_sub01-04.zip
    mv data/raw/ds000117_R1.0.0/* data/raw
    rm -rf data/raw/ds000117_R1.0.0
fi
if ! test -f data/raw/ds000117_R1.0.0_derivatives_sub01-04.zip; then
    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_derivatives_sub01-04.zip"
    unzip data/raw/ds000117_R1.0.0_derivatives_sub01-04.zip
    mv data/raw/ds000117_R1.0.0/* data/raw
    rm -rf data/raw/ds000117_R1.0.0
fi
#if ! test -f data/raw/ds000117_R1.0.0_sub05-08.zip; then
#    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_sub05-08.zip"
#    unzip data/raw/ds000117_R1.0.0_sub05-08.zip
#    mv data/raw/ds000117_R1.0.0/* data/raw
#    rm -rf data/raw/ds000117_R1.0.0
#fi
#if ! test -f data/raw/ds000117_R1.0.0_derivatives_sub05-08.zip; then
#    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_derivatives_sub05-08.zip"
#    unzip data/raw/ds000117_R1.0.0_derivatives_sub05-08.zip
#    mv data/raw/ds000117_R1.0.0/* data/raw
#    rm -rf data/raw/ds000117_R1.0.0
#fi
#if ! test -f data/raw/ds000117_R1.0.0_sub09-12.zip; then
#    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_sub09-12.zip"
#    unzip data/raw/ds000117_R1.0.0_sub09-12.zip
#    mv data/raw/ds000117_R1.0.0/* data/raw
#    rm -rf data/raw/ds000117_R1.0.0
#fi
#if ! test -f data/raw/ds000117_R1.0.0_derivatives_sub09-12.zip; then
#    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_derivatives_sub09-12.zip"
#    unzip data/raw/ds000117_R1.0.0_derivatives_sub09-12.zip
#    mv data/raw/ds000117_R1.0.0/* data/raw
#    rm -rf data/raw/ds000117_R1.0.0
#fi
#if ! test -f data/raw/ds000117_R1.0.0_sub13-16.zip; then
#    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_sub13-16.zip"
#    unzip data/raw/ds000117_R1.0.0_sub13-16.zip
#    mv data/raw/ds000117_R1.0.0/* data/raw
#    rm -rf data/raw/ds000117_R1.0.0
#fi
#if ! test -f data/raw/ds000117_R1.0.0_derivatives_sub13-16.zip; then
#    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_derivatives_sub13-16.zip"
#    unzip data/raw/ds000117_R1.0.0_derivatives_sub13-16.zip
#    mv data/raw/ds000117_R1.0.0/* data/raw
#    rm -rf data/raw/ds000117_R1.0.0
#fi

# Download metadata
if ! test -f data/raw/ds000117_R1.0.0_metadata.zip; then
    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_metadata.zip"
    unzip data/raw/ds000117_R1.0.0_metadata.zip   
    mv data/raw/ds000117_R1.0.0/* data/raw
    rm -rf data/raw/ds000117_R1.0.0
fi

# Download stimuli
if ! test -f data/raw/ds000117_R1.0.0_stimuli.zip; then
    wget -P data/raw "https://s3.amazonaws.com/openneuro/ds000117/ds000117_R1.0.0/compressed/ds000117_R1.0.0_stimuli.zip"
    unzip data/raw/ds000117_R1.0.0_stimuli.zip
    mv data/raw/ds000117_R1.0.0/* data/raw
    rm -rf data/raw/ds000117_R1.0.0
fi