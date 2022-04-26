import mne
import sys
import numpy
import os


def save_meg_coords_and_names(processed_folder):
    """
    Extracts the MEG 3D coords from the first run of the first subject (which is fine since they
    are the same for every subject and run), transforms them to the head coordinate frame and saves them to the processed folder
    together with the channel names
    """
    raw = mne.io.read_raw_fif(
        processed_folder + "/data/processed/subject1/run1/processed.fif"
    )

    # Extract and collect
    coords = []
    names = []
    for channel_info in raw.info["chs"]:
        channel_name = channel_info["ch_name"]
        if "MEG" in channel_info["ch_name"]:
            coords.append(
                mne.transforms.apply_trans(
                    raw.info["dev_head_t"], channel_info["loc"][:3]
                )
            )
            names.append(channel_name)

    # Save
    numpy.save(processed_folder + "/data/processed/meg_coords.npy", coords)
    numpy.save(processed_folder + "/data/processed/meg_names.npy", names)


def save_eeg_names(processed_folder):
    """
    Extracts the EEG channel names from the first run of the first subject (which is fine since they
    are the same for every subject and run), the EEG 3D coords are extracted during preprocessing as they are run specific
    """

    # Extract
    raw = mne.io.read_raw_fif(
        processed_folder + "/data/processed/subject1/run1/processed.fif"
    )
    names = [ch["ch_name"] for ch in raw.info["chs"] if "EEG" in ch["ch_name"]]
    print(names)
    print(len(names))

    # Save
    numpy.save(processed_folder + "/data/processed/eeg_names.npy", names)