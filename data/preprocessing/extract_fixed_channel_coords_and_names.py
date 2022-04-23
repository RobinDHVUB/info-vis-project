import mne
import numpy


def save_meg_coords_and_names():
    """
    Extracts the MEG 3D coords from the first run of the first subject (which is fine since they
    are the same for every subject and run), transforms them to the head coordinate frame and saves them to the processed folder
    together with the channel names
    """
    raw = mne.io.read_raw_fif("data/processed/sub001/run0/processed.fif")

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
    numpy.save("data/processed/meg_coords.npy", coords)
    numpy.save("data/processed/meg_names.npy", names)


def save_eeg_names():
    """
    Extracts the EEG channel names from the first run of the first subject (which is fine since they
    are the same for every subject and run), the EEG 3D coords are extracted during preprocessing as they are run specific
    """

    # Extract
    raw = mne.io.read_raw_fif("data/processed/sub001/run0/processed.fif")
    names = mne.channels.find_layout(raw.info, ch_type="eeg").names

    # Save
    numpy.save("data/processed/eeg_names.npy", names)


if __name__ == "__main__":
    save_meg_coords_and_names()
    save_eeg_names()
