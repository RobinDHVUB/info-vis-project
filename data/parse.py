import mne
import numpy
from scipy import signal


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
group_names = [
    "Frontal lobe",
    "Parietal lobe",
    "Temporal lobe (L)",
    "Temporal lobe (R)",
    "Occipital lobe",
]

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


def group_averages(runs, eeg_groups, meg_groups):
    """
    Parses and returns channel group averages for a given run
    ---
    input:
        raw runs
        dict of eeg channels
        dict of meg channels
    ---
    output:
        list of runs each with dict of EEG runs average per group
        list of runs each with dict of EEG psd per group
        list of runs each with dict of MEG runs average per group
        list of runs each with dict of MEG psd per group
    """

    # For each run
    eeg_groups_data_per_run = []
    eeg_groups_psd_per_run = []
    meg_groups_data_per_run = []
    meg_groups_psd_per_run = []
    for run in runs:

        # Split per EEG group
        eeg_groups_data = {}
        eeg_groups_psd = {}
        for group_name, group_channels in eeg_groups.items():
            assert len(group_channels) > 0
            data = run.get_data(picks=group_channels, units="uV")
            eeg_groups_data[group_name] = numpy.mean(data, axis=0)
            eeg_groups_psd[group_name] = signal.welch(data, 145)

        eeg_groups_data_per_run.append(eeg_groups_data)
        eeg_groups_psd_per_run.append(eeg_groups_psd)

        # Split per MEG group
        meg_groups_data = {}
        meg_groups_psd = {}
        for group_name, group_channels in meg_groups.items():
            assert len(group_channels) > 0
            data = run.get_data(picks=group_channels, units="fT")
            meg_groups_data[group_name] = numpy.mean(data, axis=0)
            meg_groups_psd[group_name] = signal.welch(data, 145)

        meg_groups_data_per_run.append(meg_groups_data)
        meg_groups_psd_per_run.append(meg_groups_psd)

    # Return groups
    return (
        eeg_groups_data_per_run,
        eeg_groups_psd_per_run,
        meg_groups_data_per_run,
        meg_groups_psd_per_run,
    )


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


def avg_windows(runs, event_ids, tmin, tmax, EEG_groups, MEG_groups):
    """
    Parses and returns windows for a given subject's run
    ---
    input:
        raw runs
        list of event ids to window over
        time to cut before the event (must be >= minimum_min)
        time to cut after the event  (must be <= maximum_max)
        dict of eeg channels
        dict of meg channels
    ---
    output
        dict of EEG runs windowed average per group
        dict of EEG psd windowed average per group
        dict of MEG runs windowed average per group
        dict of MEG psd windowed average per group
    """

    # Window
    windows = mne.concatenate_epochs(
        [
            mne.Epochs(
                run,
                numpy.insert(extract_events(run, event_ids), 1, 0, axis=1),
                picks=[channel for group in EEG_groups.values() for channel in group]
                + [channel for group in MEG_groups.values() for channel in group],
                tmin=tmin,
                tmax=tmax,
                preload=True,
            )
            for run in runs
        ]
    )

    # Split per EEG group
    eeg_groups_windows = {}
    eeg_groups_psd = {}
    for group_name, group_channels in EEG_groups.items():
        avg_window = numpy.mean(
            windows.get_data(picks=group_channels, units="uV"), axis=0
        )
        eeg_groups_windows[group_name] = numpy.mean(
            avg_window,
            axis=0,
        )
        eeg_groups_psd[group_name] = signal.welch(avg_window, 145)

    # Split per MEG group
    meg_groups_windows = {}
    meg_groups_psd = {}
    for group_name, group_channels in MEG_groups.items():
        avg_window = numpy.mean(
            windows.get_data(picks=group_channels, units="fT"), axis=0
        )
        meg_groups_windows[group_name] = numpy.mean(
            avg_window,
            axis=0,
        )
        meg_groups_psd[group_name] = signal.welch(avg_window, 145)

    return eeg_groups_windows, eeg_groups_psd, meg_groups_windows, meg_groups_psd
