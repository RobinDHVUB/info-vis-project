import mne
import os

# Create ICA-processed folder
os.mkdir("/data/brussel/102/vsc10248/data")
os.mkdir("/data/brussel/102/vsc10248/data/processed")

# Loop over subjects
for subject_folder in os.listdir("/scratch/brussel/102/vsc10248/data/raw"):

    # Make folder for subject processed
    os.mkdir("/data/brussel/102/vsc10248/data/processed/" + subject_folder)

    # Loop over runs
    for run_id, run_file in enumerate(os.listdir("/scratch/brussel/102/vsc10248/data/raw/" + subject_folder)):

        # Read raw
        raw = mne.io.read_raw_fif("/scratch/brussel/102/vsc10248/data/raw/" + subject_folder + "/" + run_file)

        # Pick MEG and EEG
        raw.pick_types(meg='mag', eeg=True, stim=True)
        print(raw)

        # Resample according to Shannon-Nyquist and highest freq band
        raw.resample(250)

        # Bandpass filter between lowest and highest of freq bands
        raw.filter(l_freq=0, h_freq=100)
        raw.notch_filter(50)

        # Save
        raw.save("/data/brussel/102/vsc10248/data/processed/" + subject_folder + "/" + str(run_id) + ".fif")