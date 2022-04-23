import mne
import numpy


def save_meg_coords_and_names():
    """
    Extracts the MEG 3D coords from the first run of the first subject (which is fine since they
    are the same for every subject and run), transforms them to the head coordinate frame and saves them to the processed folder
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


if __name__ == "__main__":
    save_meg_coords_and_names()
