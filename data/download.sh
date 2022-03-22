#!/bin/bash

# Download subject data
if ! test -f data/raw/sub1; then
    mkdir data/raw/sub1
    wget -P data/raw "http://openfmri.s3.amazonaws.com/tarballs/ds117_R0.1.1_sub001_raw.tgz"
    tar xvzf data/raw/ds117_R0.1.1_sub001_raw.tgz data/raw
    mv data/raw/ds117_R0.1.1_sub001_raw/MEG/* data/raw/sub1
    rm -rf data/raw/ds117_R0.1.1_sub001_raw data/raw/*.tgz
fi