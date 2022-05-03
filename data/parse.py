import mne
import numpy
import time
import os
import json
from datetime import datetime


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

# BUILD_JSON -> TODO should still be cleaned up
def age(birthdate_array):
    """
    TODO: add doc
    """

    # convert the date array to a string format
    birthdate_str = "-".join([str(int) for int in birthdate_array])

    # convert birthdate string to a date object
    birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')

    # get today's date
    today = datetime.today()

    # compute the age
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def build_subjects_json():
    """
    TODO: add doc
    """

    directory_path = "data/processed/"

    meg_coords = parse_meg_coords()
    meg_x = meg_coords[:, 0].tolist()
    meg_y = meg_coords[:, 1].tolist()
    meg_z = meg_coords[:, 2].tolist()

    meg_mesh = 0.95 * meg_coords
    meg_mesh_x = meg_mesh[:, 0].tolist()
    meg_mesh_y = meg_mesh[:, 1].tolist()
    meg_mesh_z = meg_mesh[:, 2].tolist()

    meg_names = parse_meg_names().tolist()
    meg_types = ["visual" for _ in range(0,10)]
    meg_types.extend(["motory" for _ in range(0,10)])
    meg_types.extend(["sensory" for _ in range(0, len(meg_names) - 20)])

    eeg_names = parse_eeg_names().tolist()
    eeg_types = ["visual" for _ in range(0, 10)]
    eeg_types.extend(["motory" for _ in range(0, 10)])
    eeg_types.extend(["sensory" for _ in range(0, len(eeg_names) - 20)])

    # meg data and eeg are fixed, so include it only once in the JSON
    subject_data = {'meg_names': parse_meg_names().tolist(),
                    'meg_types': meg_types,
                    'eeg_types': eeg_types,
                    'eeg_names': parse_eeg_names().tolist(),
                    'meg_coords': [meg_x, meg_y, meg_z],
                    'meg_mesh_coords': [meg_mesh_x, meg_mesh_y, meg_mesh_z]
                    }

    # collect the full paths to all the folders with a subject
    subject_folder_paths = []
    subject_ids = []
    for subject_folder in os.listdir(directory_path):
        full_path = os.path.join(directory_path, subject_folder)
        # ignore files, only folders contain subjects
        if os.path.isdir(full_path):
            subject_ids.append(subject_folder.removeprefix("subject"))
            subject_folder_paths.append(full_path)

    # initialize the dict of subjects
    subjects = []

    # go over each subject folder and build an easily usable representation (for JS)
    for subject_path, subject_id in zip(subject_folder_paths, subject_ids):
        # gather all subject specific info
        with open(os.path.join(subject_path, 'info.json'), mode='rb') as info_file:
            subject_info = json.load(info_file)

            eeg_coords = parse_eeg_coords(subject_id, 1)
            mesh_coords = 0.95 * eeg_coords

            eeg_x = eeg_coords[:,0].tolist()
            eeg_y = eeg_coords[:,1].tolist()
            eeg_z = eeg_coords[:,2].tolist()

            mesh_x = mesh_coords[:,0].tolist()
            mesh_y = mesh_coords[:,1].tolist()
            mesh_z = mesh_coords[:,2].tolist()

            subjects.append({
                "id": subject_id,
                "name": "subject " + str(subject_id),
                "age": age(subject_info["birthday"]),
                "sex": "m" if subject_info["sex"] == 1 else "f",
                "hand": "r" if subject_info["hand"] == 1 else "l",
                # eeg coords can differ per subject
                "eeg_coords": [eeg_x, eeg_y, eeg_z],
                "mesh_coords": [mesh_x, mesh_y, mesh_z],
            })

    # store the subject info
    subject_data['subjects'] = subjects

    # generate and save the JSON object with all subject info
    json_object = json.dumps(subject_data, indent=4)
    with open(os.path.join(directory_path, "subject_data.json"), "w") as outfile:
        outfile.write(json_object)

# -----
# PSD
# -----


#def parse_windows(subject, run, eeg_channels, meg_channels, tmin, tmax):