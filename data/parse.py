import mne
import numpy
import time

# -----
# MEG
# -----


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


# -----
# EEG
# -----

def parse_eeg_coords(subject, run):
    """
    Parses and returns the saved EEG channel 3D coords, they are different for every subject and run
    so a subject and run should be provided
    ---
    input: subject number [1-19], run number [1-6]
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


# ----
# RUNS
# ----


def parse_run(subject, run, eeg_channels, meg_channels):
    """
    Parses and returns windows for a given subject's run
    ---
    input:
        subject number [1-19]
        run number [1-6]
        list of eeg channels (those returned by parse_eeg_names)
        list of meg channels (those return by parse_meg_names)
    ---
    output:
        EEG run in microvolt (n_eeg_channels, n_samples)
        MEG run in femtotesla ( n_meg_channels, n_samples)
        events (n_events,3) -> first column is event time in samples, third column is event id, ignore the second column
    """
    raw = mne.io.read_raw_fif(
        "data/processed/subject" + str(subject) + "/run" + str(run) + "/processed.fif"
    )
    return (
        raw.get_data(picks=eeg_channels, units="uV") if len(eeg_channels) > 0 else [],
        raw.get_data(picks=meg_channels, units="fT") if len(meg_channels) > 0 else [],
        mne.find_events(raw, stim_channel=["STI101"], min_duration=2) if (len(eeg_channels) > 0 and len(meg_channels) > 0) else [],
    )

# -----
# WINDOWS
# -----


def parse_windows(subject, run, eeg_channels, meg_channels, tmin, tmax):
    """
    Parses and returns windows for a given subject's run
    ---
    input:
        subject number [1-19]
        run number [1-6]
        list of eeg channels (those returned by parse_eeg_names)
        list of meg channels (those return by parse_meg_names)
        time to cut before the event
        time to cut after the event
    ---
    output:
        EEG windows in microvolt (n_windows, n_eeg_channels, n_samples)
        MEG windows in femtotesla (n_windows, n_meg_channels, n_samples)
    """
    raw = mne.io.read_raw_fif(
        "data/processed/subject" + str(subject) + "/run" + str(run) + "/processed.fif"
    )
    windows = mne.Epochs(
        raw,
        mne.find_events(raw, stim_channel=["STI101"]),
        picks=eeg_channels + meg_channels,
        tmin=tmin,
        tmax=tmax,
        preload=True,
    )

    return windows.get_data(picks=eeg_channels, units="uV"), windows.get_data(
        picks=meg_channels, units="fT"
    )


# -----
# PSD
# -----


#def parse_windows(subject, run, eeg_channels, meg_channels, tmin, tmax):