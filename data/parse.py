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
    17: "Initial Scrambled Face",
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

    return (
        raw.get_data(picks=eeg_channels, units="uV") if len(eeg_channels) > 0 else [],
        raw.get_data(picks=meg_channels, units="fT") if len(meg_channels) > 0 else [],
        extract_events(raw)
    )

def extract_events(raw, event_ids=None):
    
    # Get events from raw
    events = mne.find_events(raw, stim_channel=["STI101"])
    
    # Select 
    selected_events = []
    selection = event_names.keys() if event_ids is None else event_ids
    for event in events:
        if event[1] in selection:
            selected_events.append([event[0], event[1]])
        elif event[2] in selection:
            selected_events.append([event[0], event[2]])

    return selected_events


# -----
# WINDOWS
# -----


def parse_windows(subject, run, eeg_channels, meg_channels, event_ids, tmin, tmax):
    """
    Parses and returns windows for a given subject's run
    ---
    input:
        subject number [1-19]
        run number [1-6]
        list of eeg channels
        list of meg channels
        list of event ids to average over
        time to cut before the event (must be >= minimum_min)
        time to cut after the event  (must be <= maximum_max)
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
        numpy.insert(extract_events(raw, event_ids), 1, 0, axis=1),
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