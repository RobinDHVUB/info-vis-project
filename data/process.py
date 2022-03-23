import mne
import os

# Create processed folder
os.mkdir("data/competition/processed")

# Loop over subjects
for subject_folder in os.listdir("data/raw"):

    # Loop over runs
    for run_id, run_file in enumerate(os.listdir("data/raw/" + subject_folder)):

        # Read raw
        raw = mne.io.read_raw_fif("data/raw/" + subject_folder + "/" + run_file)

        # Pick MEG and EEG

        # Resample according to Shannon-Nyquist and highest freq band

        # Bandpass filter between lowest and highest of freq bands

        # ICA

        # Save
        print(raw.info)