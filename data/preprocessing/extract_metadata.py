import mne
import sys
import numpy
import os
import json
import pandas


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


def build_subjects_file(processed_folder):
    """
    TODO: add doc
    """

    # Read first run of first subject
    raw = mne.io.read_raw_fif(
        processed_folder + "/data/processed/subject1/run1/processed.fif"
    )

    """
        MEG COORDS AND NAMES
    """

    # Extract and collect
    meg_coords = []
    meg_names = []
    for channel_info in raw.info["chs"]:
        channel_name = channel_info["ch_name"]
        if "MEG" in channel_info["ch_name"]:
            meg_coords.append(
                mne.transforms.apply_trans(
                    raw.info["dev_head_t"], channel_info["loc"][:3]
                )
            )
            meg_names.append(channel_name)

    meg_x = meg_coords[:, 0].tolist()
    meg_y = meg_coords[:, 1].tolist()
    meg_z = meg_coords[:, 2].tolist()

    meg_mesh = 0.95 * meg_coords
    meg_mesh_x = meg_mesh[:, 0].tolist()
    meg_mesh_y = meg_mesh[:, 1].tolist()
    meg_mesh_z = meg_mesh[:, 2].tolist()

    meg_types = ["visual" for _ in range(0, 10)]
    meg_types.extend(["motory" for _ in range(0, 10)])
    meg_types.extend(["sensory" for _ in range(0, len(meg_names) - 20)])

    """
        EEG NAMES
    """

    eeg_names = [ch["ch_name"] for ch in raw.info["chs"] if "EEG" in ch["ch_name"]]
    eeg_types = ["visual" for _ in range(0, 10)]
    eeg_types.extend(["motory" for _ in range(0, 10)])
    eeg_types.extend(["sensory" for _ in range(0, len(eeg_names) - 20)])

    """
        SUBJECT DATA
    """

    # Read given metadata
    metadata = pandas.DataFrame.from_csv(processed_folder + "data/raw/participants.tsv", sep='\t', index_col=False)
    metadata = [item for item in metadata.T.to_dict().values()]
    print(metadata)

    # meg data and eeg are fixed, so include it only once in the JSON
    subject_data = {
        "meg_names": meg_names,
        "meg_types": meg_types,
        "eeg_types": eeg_types,
        "eeg_names": eeg_names,
        "meg_coords": [meg_x, meg_y, meg_z],
        "meg_mesh_coords": [meg_mesh_x, meg_mesh_y, meg_mesh_z],
    }

    # collect the full paths to all the folders with a subject
    subject_folder_paths = []
    subject_ids = []
    for subject_folder in os.listdir(processed_folder + "/data/processed"):
        full_path = processed_folder + "/data/processed/" + subject_folder
        # ignore files, only folders contain subjects
        if os.path.isdir(full_path):
            subject_ids.append(subject_folder.removeprefix("subject"))
            subject_folder_paths.append(full_path)

    # initialize the dict of subjects
    subjects = []

    # Go over each subject folder and build an easily usable representation (for JS)
    for subject_folder in os.listdir(processed_folder + "/data/processed"):

        # Define subject number
        subject_id = str(int(subject_folder[-2:]))

        # gather all subject specific info
        with open(
            os.path.join(
                processed_folder + "/data/processed/" + subject_folder + "/info.json"
            ),
            mode="rb",
        ) as info_file:
            subject_info = json.load(info_file)

            eeg_coords = numpy.load(
                "data/processed/"
                + subject_folder
                + "/run1/eeg_coords.npy"
            )
            mesh_coords = 0.95 * eeg_coords

            eeg_x = eeg_coords[:, 0].tolist()
            eeg_y = eeg_coords[:, 1].tolist()
            eeg_z = eeg_coords[:, 2].tolist()

            mesh_x = mesh_coords[:, 0].tolist()
            mesh_y = mesh_coords[:, 1].tolist()
            mesh_z = mesh_coords[:, 2].tolist()

            subjects.append(
                {
                    "id": subject_id,
                    "name": "subject " + str(subject_id),
                    "age": metadata[subject_id-1]["age"],
                    "sex": "m" if subject_info["sex"] == 1 else "f",
                    "hand": "r" if subject_info["hand"] == 1 else "l",
                    # eeg coords can differ per subject
                    "eeg_coords": [eeg_x, eeg_y, eeg_z],
                    "mesh_coords": [mesh_x, mesh_y, mesh_z],
                }
            )

    # store the subject info
    subject_data["subjects"] = subjects

    # generate and save the JSON object with all subject info
    json_object = json.dumps(subject_data, indent=4)
    with open(processed_folder + "data/processed/subject_data.json", "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    build_subjects_file(str(sys.argv[1:]))