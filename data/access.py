import mne
import numpy
from scipy import signal


# -----
# Constants
# -----

# Event names
event_names = {1: "Famous", 2: "Scrambled", 3: "Unfamiliar"}

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

# Sampling frequency
sfreq = 145

# Average downsampled sampling frequency
avg_sfreq = 45


# ----
# RUNS
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
        "data/processed/subject" + str(subject) + "/run" + str(run) + "/processed_downsampled.fif",
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


def group_averages(runs, downsampled_runs, eeg_groups, meg_groups):
    """
    Parses and returns channel group averages for a given run, downsampled with a given factor
    ---
    input:
        raw runs
        downsampled runs
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
    for run, downsampled_run in zip(runs, downsampled_runs):

        # Split per EEG group
        eeg_groups_data = {}
        eeg_groups_psd = {}
        for group_name, group_channels in eeg_groups.items():
            assert len(group_channels) > 0

            # Non-downsampled
            data = run.get_data(picks=group_channels, units="uV")

            # Store psd of non-downsampled
            eeg_groups_psd[group_name] = signal.welch(data, 145)

            # Downsampled
            downsampled_data = downsampled_run.get_data(picks=group_channels, units="uV")

            # Store data of downsampled
            eeg_groups_data[group_name] = numpy.mean(downsampled_data, axis=0)


        eeg_groups_data_per_run.append(eeg_groups_data)
        eeg_groups_psd_per_run.append(eeg_groups_psd)

        # Split per MEG group
        meg_groups_data = {}
        meg_groups_psd = {}
        for group_name, group_channels in meg_groups.items():
            assert len(group_channels) > 0

            # Non-downsampled
            data = run.get_data(picks=group_channels, units="fT")

            # Store psd of non-downsampled
            eeg_groups_psd[group_name] = signal.welch(data, sfreq)

            # Downsampled
            downsampled_data = downsampled_run.get_data(picks=group_channels, units="fT")

            # Store data of downsampled
            eeg_groups_data[group_name] = numpy.mean(downsampled_data, axis=0)

        meg_groups_data_per_run.append(meg_groups_data)
        meg_groups_psd_per_run.append(meg_groups_psd)

        # Get events from downsampled version
        events_per_run.append([transform_event(event) for event in mne.events_from_annotations(downsampled_run)[0]])

    # Return collected data
    return (
        eeg_groups_data_per_run,
        eeg_groups_psd_per_run,
        meg_groups_data_per_run,
        meg_groups_psd_per_run,
        events_per_run,
    )

def transform_event(event):
    return (event[0], event[2])

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
