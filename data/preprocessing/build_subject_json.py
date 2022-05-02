import mne
import sys
import numpy
import os
import json
from datetime import datetime

from parse import parse_meg_coords, parse_meg_names, parse_eeg_names, parse_eeg_coords




def age(birthdate_array):
    """
    TODO: add doc
    """

    print("inside")

    # convert the date array to a string format
    birthdate_str = "-".join([str(int) for int in birthdate_array])

    # convert birthdate string to a date object
    birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')

    # get today's date
    today = datetime.today()

    # compute the age
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def build_subjects_file():
    """
    TODO: add doc
    """

    # TODO: directory path?
    directory_path = "../processed"

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

    print(subject_data)

    # generate and save the JSON object with all subject info
    json_object = json.dumps(subject_data, indent=4)
    with open(os.path.join(directory_path, "subject_data.json"), "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    build_subjects_file()