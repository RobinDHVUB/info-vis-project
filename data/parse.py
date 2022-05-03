import mne
import numpy


# -----
# Constants
# -----

# Event id -> event name
event_names = {
    5: "Initial Famous Face",
    6: "Immediate Repeat Famous Face",
    7: "Delayed Repeat Famous Face",
    13: "Initial Unfamiliar Face",
    14: "Immediate Repeat Unfamiliar Face",
    15: "Delayed Repeat Unfamiliar Face",
    17: "Initial Scambled Face",
    18: "Immediate Repeat Scrambled Face",
    19: "Delayed Repeat Scrambled Face",
}

# Duration of events in seconds
event_duration = 0.8

# Windowing limits in seconds 
minimum_min = 1.5 # (interstimulus interval is 1.7 so 1.5 for safety)
maximum_max = 1.5 


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

    # Extract events
    events = mne.find_events(raw, stim_channel=["STI101"])
    correct_events = []
    for event in events:
        if event[1] in event_names.keys():
            correct_events.append([event[0], event[1]])
        elif event[2] in event_names.keys():
            correct_events.append([event[0], event[2]])

    return (
        raw.get_data(picks=eeg_channels, units="uV") if len(eeg_channels) > 0 else [],
        raw.get_data(picks=meg_channels, units="fT") if len(meg_channels) > 0 else [],
        correct_events
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
        EEG windows AVG in microvolt (n_eeg_channels, n_samples)
        EEG windows STD in microvolt (n_eeg_channels, n_samples)
        MEG windows AVG in femtotesla (n_meg_channels, n_samples)
        MEG windows STD in femtotesla (n_meg_channels, n_samples)
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

    eeg_windows = windows.get_data(picks=eeg_channels, units="uV")
    meg_windows = windows.get_data(picks=meg_channels, units="fT")

    return numpy.mean(eeg_windows, axis=0), numpy.std(eeg_windows, axis=0), numpy.mean(meg_windows, axis=0), numpy.std(meg_windows, axis=0)


# -----
# PSD
# -----


# def parse_windows(subject, run, eeg_channels, meg_channels, tmin, tmax):
# 