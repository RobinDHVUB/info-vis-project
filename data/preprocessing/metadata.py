import mne
import os
import numpy
import json

# Verify if ICA_processed folder exists
if not os.path.isdir("data/ICA_processed"):
    print("ICA_processed folder not found, process first!")
    quit()

# Create metadata folder
if os.path.isdir("data/metadata"):
    print("metadata folder exists, clear first")
    quit()
else:
    os.mkdir("data/metadata")

# Loop over subjects
for subject_folder in os.listdir("data/ICA_processed"):

    # Make folder for subject metadata
    os.mkdir("data/metadata/" + subject_folder)

    # Read raw of first run
    raw = mne.io.read_raw_fif("data/ICA_processed/" + subject_folder + "/0.fif")

    # Get subject info
    # See: https://mne.tools/dev/generated/mne.Info.html
    subject_info = raw.info["subject_info"]

    # Save to file
    with open("data/metadata/" + subject_folder + "/info.json", "w") as outfile:
        json.dump(subject_info, outfile)

    # Get MEG coords
    meg_coords = mne.channels.find_layout(raw.info, ch_type="mag").pos
    meg_names = mne.channels.find_layout(raw.info, ch_type="mag").names

    # Save to file
    numpy.save("data/metadata/" + subject_folder + "/meg_coords.npy", meg_coords)
    numpy.save("data/metadata/" + subject_folder + "/meg_names.npy", meg_names)

    # Get EEG coords
    eeg_coords = mne.channels.find_layout(raw.info, ch_type="eeg").pos
    eeg_names = mne.channels.find_layout(raw.info, ch_type="eeg").names

    # Save to file
    numpy.save("data/metadata/" + subject_folder + "/eeg_coords.npy", eeg_coords)
    numpy.save("data/metadata/" + subject_folder + "/eeg_names.npy", eeg_names)
