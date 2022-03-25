import mne
import os

# Create ICA-processed folder
os.mkdir("data/ICA_processed")

# Loop over subjects
for subject_folder in os.listdir("data/processed"):

    # Make folder for subject ICA-processed
    os.mkdir("data/ICA_processed/" + subject_folder)

    # Loop over runs
    for run_id, run_file in enumerate(os.listdir("data/processed/" + subject_folder)):

        # Read raw
        raw = mne.io.read_raw_fif("data/processed/" + subject_folder + "/" + run_file)
        print(raw.info)
