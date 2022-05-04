import mne
import sys
import numpy
import os
import json
import pandas


def build_subjects_file():

    # Read first run of first subject
    raw = mne.io.read_raw_fif(
        "/scratch/brussel/102/vsc10248/data/processed/subject1/run1/processed.fif"
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
    meg_coords = numpy.stack(meg_coords, axis=0)

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
    metadata = pandas.read_csv(
        "/scratch/brussel/102/vsc10248/data/raw/participants.tsv", sep="\t", index_col=False
    )
    metadata = [item for item in metadata.T.to_dict().values()]

    # Get ages into dict
    ages = {}
    for subject_metadata in metadata:
        ages[int(subject_metadata["participant_id"][-2:])] = subject_metadata["age"]

    # meg data and eeg are fixed, so include it only once in the JSON
    subject_data = {
        "meg_names": meg_names,
        "meg_types": meg_types,
        "eeg_types": eeg_types,
        "eeg_names": eeg_names,
        "meg_coords": [meg_x, meg_y, meg_z],
        "meg_mesh_coords": [meg_mesh_x, meg_mesh_y, meg_mesh_z],
    }

    # initialize the dict of subjects
    subjects = []

    # Go over each subject folder and build an easily usable representation (for JS)
    for subject_id in sorted([int(subject_folder.removeprefix("subject")) for subject_folder in os.listdir("/scratch/brussel/102/vsc10248/data/processed")]):

        # gather all subject specific info
        with open(
            "/scratch/brussel/102/vsc10248/data/processed/subject" + subject_id + "/info.json",
            mode="rb",
        ) as info_file:
            subject_info = json.load(info_file)

            eeg_coords = numpy.load(
                "/scratch/brussel/102/vsc10248/data/processed/subject"
                + subject_id
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
                    "age": ages[subject_id],
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
    with open("/scratch/brussel/102/vsc10248/data/processed/subject_data.json", "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    build_subjects_file()
