import mne
import numpy
import json

from scipy import signal
from bokeh.palettes import Colorblind

# ----
# Subject info
# ----
def parse_metadata():
    as_dict = 0
    with open("data/processed/metadata.json") as subject_data:
        as_dict = json.load(subject_data)

    return as_dict


# -----
# Constants
# -----

# Event names
event_names = ["Famous", "Scrambled", "Unfamiliar"]
event_colors = {
    event_name: event_color
    for event_name, event_color in zip(event_names, Colorblind[3])
}

# Group names
group_names = [
    "Frontal lobe",
    "Parietal lobe",
    "Temporal lobe (L)",
    "Temporal lobe (R)",
    "Occipital lobe",
]
group_colors = {
    group_name: group_color
    for group_name, group_color in zip(
        group_names, Colorblind[8][3:]
    )
}

# Duration of events in seconds
event_duration = 0.8

# Windowing limits in seconds
minimum_min = 1.5  # (interstimulus interval is 1.7 so 1.5 for safety)
maximum_max = 1.5

# Sampling frequency
sfreq = 145

# Average downsampled sampling frequency
avg_sfreq = 45


# ----
# Runs
# ----
def parse_run(subject, run):
    """
    Parses a subject's run
    ---
    input:
        subject number [1-16]
        run number [1-6]
    ---
    output:
        raw run
        downsampled run
    """

    # Read raw run
    raw = mne.io.read_raw_fif(
        "data/processed/subject" + str(subject) + "/run" + str(run) + "/processed.fif",
        verbose=None,
    )
    annotations = mne.read_annotations(
        "data/processed/subject"
        + str(subject)
        + "/run"
        + str(run)
        + "/processed_annotations.fif",
    )
    raw.set_annotations(annotations)

    # Read downsampled run
    downsampled = mne.io.read_raw_fif(
        "data/processed/subject"
        + str(subject)
        + "/run"
        + str(run)
        + "/processed_downsampled.fif",
        verbose=None,
    )
    downsampled_annotations = mne.read_annotations(
        "data/processed/subject"
        + str(subject)
        + "/run"
        + str(run)
        + "/processed_downsampled_annotations.fif",
    )
    downsampled.set_annotations(downsampled_annotations)

    return raw, downsampled


# ----
# Group averages
# ----
def group_averages(runs, EEG_groups_assignment, MEG_groups_assignment):
    """
    Parses and returns channel group averages for a given run as well as the transformed events
    ---
    input:
        raw runs
        EEG group assignments
        MEG group assignments
    ---
    output:
        list of runs each with dict of EEG runs average per group
        list of runs each with dict of EEG psd per group
        list of runs each with dict of MEG runs average per group
        list of runs each with dict of MEG psd per group
        list of events per run
    """

    # For each run
    eeg_groups_data_per_run = []
    eeg_groups_psd_per_run = []
    meg_groups_data_per_run = []
    meg_groups_psd_per_run = []
    events_per_run = []
    for run in runs:

        # Split per EEG group
        eeg_groups_data = {}
        eeg_groups_psd = {}
        for group_name, group_channels in EEG_groups_assignment.items():
            assert len(group_channels) > 0

            data = run.get_data(picks=group_channels, units="uV")

            # Store psd
            eeg_groups_psd[group_name] = signal.welch(data, 145)

            # Store mean
            eeg_groups_data[group_name] = numpy.mean(data, axis=0)

        eeg_groups_data_per_run.append(eeg_groups_data)
        eeg_groups_psd_per_run.append(eeg_groups_psd)

        # Split per MEG group
        meg_groups_data = {}
        meg_groups_psd = {}
        for group_name, group_channels in MEG_groups_assignment.items():
            assert len(group_channels) > 0

            data = run.get_data(picks=group_channels, units="fT")

            # Store psd
            meg_groups_psd[group_name] = signal.welch(data, sfreq)

            # Store mean
            meg_groups_data[group_name] = numpy.mean(data, axis=0)

        meg_groups_data_per_run.append(meg_groups_data)
        meg_groups_psd_per_run.append(meg_groups_psd)

        # Get events from downsampled version
        events_per_run.append(extract_events(run))

    # Return collected data
    return (
        eeg_groups_data_per_run,
        eeg_groups_psd_per_run,
        meg_groups_data_per_run,
        meg_groups_psd_per_run,
        events_per_run,
    )


def extract_events(run, selection=None):

    # Get events
    events, _ = mne.events_from_annotations(run)

    # Get event ids
    selected_ids = selection if selection is not None else list(range(1, 4))

    # Transform
    transformed_events = []
    for event in events:
        if event[2] in selected_ids:
            transformed_events.append([event[0], event[2]])

    return numpy.array(transformed_events)


# -----
# Windows
# -----
def avg_windows(
    runs, event_selection, tmin, tmax, EEG_groups_assignment, MEG_groups_assignment
):
    """
    Parses and returns average window for a given subject
    ---
    input:
        raw runs
        list of event ids to window over
        time to cut before the event (must be >= minimum_min)
        time to cut after the event  (must be <= maximum_max)
        EEG group assignments
        MEG group assignments
    ---
    output
        dict of EEG runs windowed average per group
        dict of EEG psd windowed average per group
        dict of MEG runs windowed average per group
        dict of MEG psd windowed average per group
    """

    # Window
    dev_head_t = runs[0].info["dev_head_t"]
    epochs = []
    for run in runs:
        run.info["dev_head_t"] = dev_head_t
        epochs.append(
            mne.Epochs(
                run,
                numpy.insert(extract_events(run, event_selection), 1, 0, axis=1),
                tmin=tmin,
                tmax=tmax,
                preload=True,
            )
        )
    windows = mne.concatenate_epochs(epochs)

    # Split per EEG group
    eeg_groups_windows = {}
    eeg_groups_psd = {}
    for group_name, group_channels in EEG_groups_assignment.items():
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
    for group_name, group_channels in MEG_groups_assignment.items():
        avg_window = numpy.mean(
            windows.get_data(picks=group_channels, units="fT"), axis=0
        )
        meg_groups_windows[group_name] = numpy.mean(
            avg_window,
            axis=0,
        )
        meg_groups_psd[group_name] = signal.welch(avg_window, 145)

    return eeg_groups_windows, eeg_groups_psd, meg_groups_windows, meg_groups_psd
