import mne
import numpy
import os
import json
import mne_bids


def build_subjects_file():

    # Read first run of first subject
    raw = mne.io.read_raw_fif("/scratch/brussel/102/vsc10248/info-vis-data/processed/subject1/run1/processed.fif")

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
        "Temporal lobe (L)",  # MEG0111
        "Temporal lobe (L)",  # MEG0121
        "Temporal lobe (L)",  # MEG0131
        "Temporal lobe (L)",  # MEG0141
        "Temporal lobe (L)",  # MEG0211
        "Frontal lobe",  # MEG0221
        "Parietal lobe",  # MEG0231
        "Temporal lobe (L)",  # MEG0241
        "Frontal lobe",  # MEG0311
        "Frontal lobe",  # MEG0321
        "Frontal lobe",  # MEG0331
        "Frontal lobe",  # MEG0341
        "Frontal lobe",  # MEG0411
        "Frontal lobe",  # MEG0421
        "Parietal lobe",  # MEG0431
        "Parietal lobe",  # MEG0441
        "Frontal lobe",  # MEG0511
        "Frontal lobe",  # MEG0521
        "Frontal lobe",  # MEG0531
        "Frontal lobe",  # MEG0541
        "Frontal lobe",  # MEG0611
        "Frontal lobe",  # MEG0621
        "Frontal lobe",  # MEG0631
        "Frontal lobe",  # MEG0641
        "Parietal lobe",  # MEG0711
        "Parietal lobe",  # MEG0721
        "Parietal lobe",  # MEG0731
        "Parietal lobe",  # MEG0741
        "Frontal lobe",  # MEG0811
        "Frontal lobe",  # MEG0821
        "Frontal lobe",  # MEG0911
        "Frontal lobe",  # MEG0921
        "Frontal lobe",  # MEG0931
        "Frontal lobe",  # MEG0941
        "Frontal lobe",  # MEG1011
        "Frontal lobe",  # MEG1021
        "Frontal lobe",  # MEG1031
        "Frontal lobe",  # MEG1041
        "Frontal lobe",  # MEG1111
        "Frontal lobe",  # MEG1121
        "Parietal lobe",  # MEG1131
        "Parietal lobe",  # MEG1141
        "Frontal lobe",  # MEG1211
        "Frontal lobe",  # MEG1221
        "Frontal lobe",  # MEG1231
        "Frontal lobe",  # MEG1241
        "Frontal lobe",  # MEG1311
        "Temporal lobe (R)",  # MEG1321
        "Temporal lobe (R)",  # MEG1331
        "Parietal lobe",  # MEG1341
        "Temporal lobe (R)",  # MEG1411
        "Temporal lobe (R)",  # MEG1421
        "Temporal lobe (R)",  # MEG1431
        "Temporal lobe (R)",  # MEG1441
        "Temporal lobe (L)",  # MEG1511
        "Temporal lobe (L)",  # MEG1521
        "Temporal lobe (L)",  # MEG1531
        "Temporal lobe (L)",  # MEG1541
        "Temporal lobe (L)",  # MEG1611
        "Parietal lobe",  # MEG1621
        "Parietal lobe",  # MEG1631
        "Temporal lobe (L)",  # MEG1641
        "Occipital lobe",  # MEG1711
        "Temporal lobe (L)",  # MEG1721
        "Occipital lobe",  # MEG1731
        "Occipital lobe",  # MEG1741
        "Parietal lobe",  # MEG1811
        "Parietal lobe",  # MEG1821
        "Parietal lobe",  # MEG1831
        "Parietal lobe",  # MEG1841
        "Parietal lobe",  # MEG1911
        "Occipital lobe",  # MEG1921
        "Occipital lobe",  # MEG1931
        "Occipital lobe",  # MEG1941
        "Parietal lobe",  # MEG2011
        "Parietal lobe",  # MEG2021
        "Parietal lobe",  # MEG2031
        "Parietal lobe",  # MEG2041
        "Occipital lobe",  # MEG2111
        "Occipital lobe",  # MEG2121
        "Occipital lobe",  # MEG2131
        "Occipital lobe",  # MEG2141
        "Parietal lobe",  # MEG2211
        "Parietal lobe",  # MEG2221
        "Parietal lobe",  # MEG2231
        "Parietal lobe",  # MEG2241
        "Parietal lobe",  # MEG2311
        "Occipital lobe",  # MEG2321
        "Occipital lobe",  # MEG2331
        "Occipital lobe",  # MEG2341
        "Parietal lobe",  # MEG2411
        "Temporal lobe (R)",  # MEG2421
        "Temporal lobe (R)",  # MEG2431
        "Parietal lobe",  # MEG2441
        "Occipital lobe",  # MEG2511
        "Temporal lobe (R)",  # MEG2521
        "Occipital lobe",  # MEG2531
        "Occipital lobe",  # MEG2541
        "Temporal lobe (R)",  # MEG2611
        "Temporal lobe (R)",  # MEG2621
        "Temporal lobe (R)",  # MEG2631
        "Temporal lobe (R)",  # MEG2641"
    ]

    """
        EEG NAMES
    """

    eeg_names = [ch["ch_name"] for ch in raw.info["chs"] if "EEG" in ch["ch_name"]]
    eeg_types = [
        "Occipital lobe",  # EEG001
        "Frontal lobe",  # EEG002
        "Occipital lobe",  # EEG003
        "Frontal lobe",  # EEG004
        "Frontal lobe",  # EEG005
        "Frontal lobe",  # EEG006
        "Frontal lobe",  # EEG007
        "Frontal lobe",  # EEG008
        "Frontal lobe",  # EEG009
        "Frontal lobe",  # EEG010
        "Frontal lobe",  # EEG011
        "Frontal lobe",  # EEG012
        "Frontal lobe",  # EEG013
        "Frontal lobe",  # EEG014
        "Frontal lobe",  # EEG015
        "Frontal lobe",  # EEG016
        "Frontal lobe",  # EEG017
        "Temporal lobe (L)",  # EEG018
        "Temporal lobe (L)",  # EEG019
        "Frontal lobe",  # EEG020
        "Frontal lobe",  # EEG021
        "Frontal lobe",  # EEG022
        "Frontal lobe",  # EEG023
        "Frontal lobe",  # EEG024
        "Frontal lobe",  # EEG025
        "Frontal lobe",  # EEG026
        "Temporal lobe (R)",  # EEG027
        "Temporal lobe (R)",  # EEG028
        "Temporal lobe (L)",  # EEG029
        "Temporal lobe (L)",  # EEG030
        "Frontal lobe",  # EEG031
        "Frontal lobe",  # EEG032
        "Frontal lobe",  # EEG033
        "Frontal lobe",  # EEG034
        "Frontal lobe",  # EEG035
        "Frontal lobe",  # EEG036
        "Frontal lobe",  # EEG037
        "Temporal lobe (R)",  # EEG038
        "Temporal lobe (R)",  # EEG039
        "Temporal lobe (L)",  # EEG040
        "Temporal lobe (L)",  # EEG041
        "Parietal lobe",  # EEG042
        "Parietal lobe",  # EEG043
        "Parietal lobe",  # EEG044
        "Parietal lobe",  # EEG045
        "Parietal lobe",  # EEG046
        "Parietal lobe",  # EEG047
        "Parietal lobe",  # EEG048
        "Temporal lobe (R)",  # EEG049
        "Temporal lobe (R)",  # EEG050
        "Occipital lobe",  # EEG051
        "Temporal lobe (L)",  # EEG052
        "Parietal lobe",  # EEG053
        "Parietal lobe",  # EEG054
        "Parietal lobe",  # EEG055
        "Parietal lobe",  # EEG056
        "Parietal lobe",  # EEG057
        "Parietal lobe",  # EEG058
        "Parietal lobe",  # EEG059
        "Temporal lobe (R)",  # EEG060
        "Parietal lobe",  # EEG064
        "Parietal lobe",  # EEG065
        "Frontal lobe",  # EEG066
        "Frontal lobe",  # EEG067
        "Parietal lobe",  # EEG068
        "Occipital lobe",  # EEG069
        "Occipital lobe",  # EEG070
        "Occipital lobe",  # EEG071
        "Occipital lobe",  # EEG072
        "Occipital lobe",  # EEG073
        "Occipital lobe",  # EEG074
    ]

    """
        SUBJECT DATA
    """

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
                "/scratch/brussel/102/vsc10248/info-vis-data/processed"
            )
        ]
    ):

        # gather all subject specific info
        with open(
            "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
            + str(subject_id)
            + "/info.json",
            mode="rb",
        ) as info_file:
            subject_info = json.load(info_file)

            eeg_coords = numpy.load(
                "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
                + str(subject_id)
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
                    "age": subject_info["age"],
                    "sex": "m" if subject_info["sex"] == 1 else "f",
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
        "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject_data.json", "w"
    ) as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    build_subjects_file()

