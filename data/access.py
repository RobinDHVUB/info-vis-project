import mne
import numpy
from scipy import signal


# -----
# Constants
# -----

# Event names
event_names = ["Famous", "Scrambled", "Unfamiliar"]
event_colors = {
    event_name: event_color
    for event_name, event_color in zip(event_names, ["#0900ff", "#930791", "#03f0d3"])
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
        group_names, ["#ff734e", "#ffe900", "#64ea5f", "#a1a1a1", "#000000"]
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
# RUNS
# ----


def parse_run(subject, run, logger):
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


def group_averages(runs, eeg_groups, meg_groups):
    """
    Parses and returns channel group averages for a given run as well as the transformed events
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
        for group_name, group_channels in eeg_groups.items():
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
        for group_name, group_channels in meg_groups.items():
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
# WINDOWS
# -----


def avg_windows(runs, event_selection, tmin, tmax, EEG_groups, MEG_groups):
    """
    Parses and returns average window for a given subject
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
    dev_head_t = runs[0].info["dev_head_t"]
    epochs = []
    for run in runs:
        run.info["dev_head_t"] = dev_head_t
        epochs.append(
            mne.Epochs(
                run,
                numpy.insert(extract_events(run, event_selection), 1, 0, axis=1),
                picks=[channel for group in EEG_groups.values() for channel in group]
                + [channel for group in MEG_groups.values() for channel in group],
                tmin=tmin,
                tmax=tmax,
                preload=True,
            )
        )
    windows = mne.concatenate_epochs(epochs)

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
