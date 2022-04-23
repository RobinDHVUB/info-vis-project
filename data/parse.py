import mne
import numpy


def parse_meg_coords():
    """
    Parses and returns the saved MEG channel 3D coords, they are the same for every subject
    ---
    output: MEG channel coords (numpy array)
    """
    return numpy.load("data/processed/meg_coords.npy")


def parse_meg_names():
    """
    Parses and returns the saved MEG channel names, they are the same for every subject
    ---
    output: MEG channel names (numpy array)
    """
    return numpy.load("data/processed/meg_names.npy")


def parse_eeg_coords(subject, run):
    """
    Parses and returns the saved EEG channel 3D coords, they are different for every subject and run
    so a subject and run should be provided
    ---
    input: subject number [1-19], run number [0-5]
    ---
    output: EEG channel coords (numpy array)
    """
    return numpy.load(
        "data/processed/subject" + str(subject) + "/run" + str(run) + "/eeg_coords.npy"
    )


def parse_eeg_names():
    """
    Parses and returns the saved EEG channel names, they are the same for every subject and run
    ---
    output: EEG channel names (numpy array)
    """
    return numpy.load("data/processed/eeg_names.npy")
