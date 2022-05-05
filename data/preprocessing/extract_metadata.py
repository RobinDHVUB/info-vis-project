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

    meg_types = [
        "temporal lobe (L)",  # MEG0111
        "temporal lobe (L)",  # MEG0121
        "temporal lobe (L)",  # MEG0131
        "temporal lobe (L)",  # MEG0141
        "temporal lobe (L)",  # MEG0211
        "frontal lobe",  # MEG0221
        "parietal lobe",  # MEG0231
        "temporal lobe (L)",  # MEG0241
        "frontal lobe",  # MEG0311
        "frontal lobe",  # MEG0321
        "frontal lobe",  # MEG0331
        "frontal lobe",  # MEG0341
        "frontal lobe",  # MEG0411
        "frontal lobe",  # MEG0421
        "parietal lobe",  # MEG0431
        "parietal lobe",  # MEG0441
        "frontal lobe",  # MEG0511
        "frontal lobe",  # MEG0521
        "frontal lobe",  # MEG0531
        "frontal lobe",  # MEG0541
        "frontal lobe",  # MEG0611
        "frontal lobe",  # MEG0621
        "frontal lobe",  # MEG0631
        "frontal lobe",  # MEG0641
        "parietal lobe",  # MEG0711
        "parietal lobe",  # MEG0721
        "parietal lobe",  # MEG0731
        "parietal lobe",  # MEG0741
        "frontal lobe",  # MEG0811
        "frontal lobe",  # MEG0821
        "frontal lobe",  # MEG0911
        "frontal lobe",  # MEG0921
        "frontal lobe",  # MEG0931
        "frontal lobe",  # MEG0941
        "frontal lobe",  # MEG1011
        "frontal lobe",  # MEG1021
        "frontal lobe",  # MEG1031
        "frontal lobe",  # MEG1041
        "frontal lobe",  # MEG1111
        "frontal lobe",  # MEG1121
        "parietal lobe",  # MEG1131
        "parietal lobe",  # MEG1141
        "frontal lobe",  # MEG1211
        "frontal lobe",  # MEG1221
        "frontal lobe",  # MEG1231
        "frontal lobe",  # MEG1241
        "frontal lobe",  # MEG1311
        "temporal lobe (R)",  # MEG1321
        "temporal lobe (R)",  # MEG1331
        "parietal lobe",  # MEG1341
        "temporal lobe (R)",  # MEG1411
        "temporal lobe (R)",  # MEG1421
        "temporal lobe (R)",  # MEG1431
        "temporal lobe (R)",  # MEG1441
        "temporal lobe (L)",  # MEG1511
        "temporal lobe (L)",  # MEG1521
        "temporal lobe (L)",  # MEG1531
        "temporal lobe (L)",  # MEG1541
        "temporal lobe (L)",  # MEG1611
        "parietal lobe",  # MEG1621
        "parietal lobe",  # MEG1631
        "temporal lobe (L)",  # MEG1641
        "occipital lobe",  # MEG1711
        "temporal lobe (L)",  # MEG1721
        "occipital lobe",  # MEG1731
        "occipital lobe",  # MEG1741
        "parietal lobe",  # MEG1811
        "parietal lobe",  # MEG1821
        "parietal lobe",  # MEG1831
        "parietal lobe",  # MEG1841
        "parietal lobe",  # MEG1911
        "occipital lobe",  # MEG1921
        "occipital lobe",  # MEG1931
        "occipital lobe",  # MEG1941
        "parietal lobe",  # MEG2011
        "parietal lobe",  # MEG2021
        "parietal lobe",  # MEG2031
        "parietal lobe",  # MEG2041
        "occipital lobe",  # MEG2111
        "occipital lobe",  # MEG2121
        "occipital lobe",  # MEG2131
        "occipital lobe",  # MEG2141
        "parietal lobe",  # MEG2211
        "parietal lobe",  # MEG2221
        "parietal lobe",  # MEG2231
        "parietal lobe",  # MEG2241
        "parietal lobe",  # MEG2311
        "occipital lobe",  # MEG2321
        "occipital lobe",  # MEG2331
        "occipital lobe",  # MEG2341
        "parietal lobe",  # MEG2411
        "temporal lobe (R)",  # MEG2421
        "temporal lobe (R)",  # MEG2431
        "parietal lobe",  # MEG2441
        "occipital lobe",  # MEG2511
        "temporal lobe (R)",  # MEG2521
        "occipital lobe",  # MEG2531
        "occipital lobe",  # MEG2541
        "temporal lobe (R)",  # MEG2611
        "temporal lobe (R)",  # MEG2621
        "temporal lobe (R)",  # MEG2631
        "temporal lobe (R)",  # MEG2641"
    ]
    meg_types = ["visual" for _ in range(0, 10)]
    meg_types.extend(["motory" for _ in range(0, 10)])
    meg_types.extend(["sensory" for _ in range(0, len(meg_names) - 20)])

    """
        EEG NAMES
    """

    eeg_names = [ch["ch_name"] for ch in raw.info["chs"] if "EEG" in ch["ch_name"]]
    eeg_types = [
        "occipital lobe",  # EEG001
        "frontal lobe",  # EEG002
        "occipital lobe",  # EEG003
        "frontal lobe",  # EEG004
        "frontal lobe",  # EEG005
        "frontal lobe",  # EEG006
        "frontal lobe",  # EEG007
        "frontal lobe",  # EEG008
        "frontal lobe",  # EEG009
        "frontal lobe",  # EEG010
        "frontal lobe",  # EEG011
        "frontal lobe",  # EEG012
        "frontal lobe",  # EEG013
        "frontal lobe",  # EEG014
        "frontal lobe",  # EEG015
        "frontal lobe",  # EEG016
        "frontal lobe",  # EEG017
        "temporal lobe (L)",  # EEG018
        "temporal lobe (L)",  # EEG019
        "frontal lobe",  # EEG020
        "frontal lobe",  # EEG021
        "frontal lobe",  # EEG022
        "frontal lobe",  # EEG023
        "frontal lobe",  # EEG024
        "frontal lobe",  # EEG025
        "frontal lobe",  # EEG026
        "temporal lobe (R)",  # EEG027
        "temporal lobe (R)",  # EEG028
        "temporal lobe (L)",  # EEG029
        "temporal lobe (L)",  # EEG030
        "frontal lobe",  # EEG031
        "frontal lobe",  # EEG032
        "frontal lobe",  # EEG033
        "frontal lobe",  # EEG034
        "frontal lobe",  # EEG035
        "frontal lobe",  # EEG036
        "frontal lobe",  # EEG037
        "temporal lobe (R)",  # EEG038
        "temporal lobe (R)",  # EEG039
        "temporal lobe (L)",  # EEG040
        "temporal lobe (L)",  # EEG041
        "parietal lobe",  # EEG042
        "parietal lobe",  # EEG043
        "parietal lobe",  # EEG044
        "parietal lobe",  # EEG045
        "parietal lobe",  # EEG046
        "parietal lobe",  # EEG047
        "parietal lobe",  # EEG048
        "temporal lobe (R)",  # EEG049
        "temporal lobe (R)",  # EEG050
        "occipital lobe",  # EEG051
        "temporal lobe (L)",  # EEG052
        "parietal lobe",  # EEG053
        "parietal lobe",  # EEG054
        "parietal lobe",  # EEG055
        "parietal lobe",  # EEG056
        "parietal lobe",  # EEG057
        "parietal lobe",  # EEG058
        "parietal lobe",  # EEG059
        "temporal lobe (R)",  # EEG060
        "parietal lobe",  # EEG065
        "frontal lobe",  # EEG066
        "frontal lobe",  # EEG067
        "parietal lobe",  # EEG068
        "occipital lobe",  # EEG069
        "occipital lobe",  # EEG070
        "occipital lobe",  # EEG071
        "occipital lobe",  # EEG072
        "occipital lobe",  # EEG073
        "occipital lobe",  # EEG074
    ]
    eeg_types.extend(["motory" for _ in range(0, 10)])
    eeg_types.extend(["sensory" for _ in range(0, len(eeg_names) - 20)])

    """
        SUBJECT DATA
    """

    # Read given metadata
    metadata = pandas.read_csv(
        "/scratch/brussel/102/vsc10248/data/raw/participants.tsv",
        sep="\t",
        index_col=False,
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
        "eeg_names": eeg_names,
        "eeg_types": eeg_types,
        "meg_coords": [meg_x, meg_y, meg_z],
        "meg_mesh_coords": [meg_mesh_x, meg_mesh_y, meg_mesh_z],
    }

    # initialize the dict of subjects
    subjects = []

    # Go over each subject folder and build an easily usable representation (for JS)
    for subject_id in sorted(
        [
            int(subject_folder.removeprefix("subject"))
            for subject_folder in os.listdir(
                "/scratch/brussel/102/vsc10248/data/processed"
            )
        ]
    ):

        # gather all subject specific info
        with open(
            "/scratch/brussel/102/vsc10248/data/processed/subject"
            + subject_id
            + "/info.json",
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
    with open(
        "/scratch/brussel/102/vsc10248/data/processed/subject_data.json", "w"
    ) as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    build_subjects_file()
