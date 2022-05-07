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

# Group names
group_names = ["Frontal lobe", "Parietal lobe", "Temporal lobe (L)", "Temporal lobe (R)", "Occipital lobe"]

# Duration of events in seconds
event_duration = 0.8

# Windowing limits in seconds
minimum_min = 1.5  # (interstimulus interval is 1.7 so 1.5 for safety)
maximum_max = 1.5


# ----
# RUNS
# ----


def parse_run(subject, run):
    """
    Parses and returns windows for a given subject's run
    ---
    input:
        subject number [1-19]
        run number [1-6]
    ---
    output:
        raw run
    """

    # Read run
    raw = mne.io.read_raw_fif(
        "data/processed/subject" + str(subject) + "/run" + str(run) + "/processed.fif",
        verbose=None,
    )

    return raw 

def group_average(raw, eeg_groups, meg_groups):
    """
    Parses and returns channel group averages for a given run
    ---
    input:
        raw run
        dict of eeg channels
        dict of meg channels
    ---
    output:
        dict of EEG run average per group 
        dict of MEG run average per group
    """

    # Split per EEG group
    eeg_groups_data = {}
    for group_name, group_channels in eeg_groups.items():
        assert len(group_channels) > 0
        eeg_groups_data[group_name] = numpy.mean(raw.get_data(picks=group_channels, units="uV"), axis=0)

    # Split per MEG group
    meg_groups_data = {}
    for group_name, group_channels in meg_groups.items():
        assert len(group_channels) > 0
        meg_groups_data[group_name] = numpy.mean(raw.get_data(picks=group_channels, units="fT"), axis=0)

    # Return groups
    return eeg_groups_data, meg_groups_data


def extract_events(raw, event_ids=None):

    # Get events from raw
    events = mne.find_events(raw, stim_channel=["STI101"], min_duration=1)

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
        EEG windows AVG in microvolt    (n_eeg_channels, n_samples)
        EEG windows STD in microvolt    (n_eeg_channels, n_samples)
        EEG windows PSD                 (n_eeg_channels, n_frequencies (70))
        MEG windows AVG in femtotesla   (n_meg_channels, n_samples)
        MEG windows STD in femtotesla   (n_meg_channels, n_samples)
        MEG windows PSD                 (n_meg_channels, n_frequencies (70))
    """

    # Parse run
    raw = mne.io.read_raw_fif(
        "data/processed/subject" + str(subject) + "/run" + str(run) + "/processed.fif"
    )

    # Window
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

    # Average
    eeg_windows_avg = numpy.mean(eeg_windows, axis=0)
    meg_windows_avg = numpy.mean(meg_windows, axis=0)

    # Standard deviation
    eeg_windows_std = numpy.std(eeg_windows, axis=0)
    meg_windows_std = numpy.std(meg_windows, axis=0)

    # PSD
    psd_estimator = mne.decoding.PSDEstimator(145, fmin=1, fmax=70)
    eeg_windows_avg_psd = psd_estimator.transform(eeg_windows_avg)
    meg_windows_avg_psd = psd_estimator.transform(meg_windows_avg)

    return (
        eeg_windows_avg,
        eeg_windows_std,
        eeg_windows_avg_psd,
        meg_windows_avg,
        meg_windows_std,
        meg_windows_avg_psd,
    )
