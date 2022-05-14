import mne
import sys
import os
import json
import numpy
import mne_bids


def process_subject(subject_id):

    # Make subject folder
    os.mkdir("/scratch/brussel/102/vsc10248/info-vis-data/processed/subject" + subject_id)

    # Loop over runs
    for run_id in range(1,7):

        # Define path to files
        bids_path = mne_bids.BIDSPath(subject=subject_id.zfill(2), session="meg", task="facerecognition", datatype="meg", run=run_id, root="/scratch/brussel/102/vsc10248/info-vis-data/raw")

        # Read raw
        raw = []
        try:
            raw = mne_bids.read_raw_bids(bids_path=bids_path)
            raw.load_data()
        except:
            continue

        # Make folder for run
        os.mkdir(
            "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
            + subject_id
            + "/run"
            + str(run_id)
        )

        # Do once
        if run_id == 1:

            # Get and save subject metadata
            # See: https://mne.tools/dev/generated/mne.Info.html
            with open(
                "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
                + subject_id
                + "/info.json",
                "w",
            ) as outfile:
                json.dump(raw.info["subject_info"], outfile)

        # Get and save EEG coords (can vary per run)
        eeg_coords = [ch["loc"][:3] for ch in raw.info["chs"] if "EEG" in ch["ch_name"]]
        numpy.save(
            "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
            + subject_id
            + "/run"
            + str(run_id)
            + "/eeg_coords.npy",
            eeg_coords,
        )

        # Correct EOG and ECG channel names
        # See: https://www.nature.com/articles/sdata20151
        raw.rename_channels({"EEG061": "HEOG", "EEG062": "VEOG", "EEG063": "ECG"})
        raw.set_channel_types({"HEOG": "eog", "VEOG": "eog", "ECG": "ecg"})

        # Bandpass filter between lowest and highest of freq bands
        raw.filter(l_freq=1.0, h_freq=70)
        raw.notch_filter(50)

        # Resample according to Shannon-Nyquist and highest freq band
        raw.resample(145)

        # ICA
        ica = mne.preprocessing.ICA(n_components=16, max_iter="auto", random_state=97)
        ica.fit(raw)
        ica.exclude = []
        eog_indices, eog_scores = ica.find_bads_eog(
            raw
        )  # Use EOG to find bad components
        ecg_indices, ecg_scores = ica.find_bads_ecg(
            raw, method="correlation", threshold="auto"
        )  # Use ECG to find bad components
        plot = ica.plot_sources(
            raw, stop=10, show_scrollbars=False
        )  # Plot ICA comps for first 10 seconds
        plot.savefig(
            "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
            + subject_id
            + "/run"
            + str(run_id)
            + "/ICA.pdf"
        )
        ica.exclude = eog_indices + ecg_indices
        ica.apply(raw)  # Apply

        # Pick MEG and EEG channels
        raw.pick_types(meg="mag", eeg=True)

        # Create and save downsampled copy for average view
        downsampled = raw.copy().resample(45)
        downsampled.save(
            "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
            + subject_id
            + "/run"
            + str(run_id)
            + "/processed_downsampled.fif"
        )
        downsampled.annotations.save(
            "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
            + subject_id
            + "/run"
            + str(run_id)
            + "/processed_downsampled_annotations.fif"
        )

        # Save
        raw.save(
            "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
            + subject_id
            + "/run"
            + str(run_id)
            + "/processed.fif"
        )
        raw.annotations.save(
            "/scratch/brussel/102/vsc10248/info-vis-data/processed/subject"
            + subject_id
            + "/run"
            + str(run_id)
            + "/processed_annotations.fif"
        )

if __name__ == "__main__":
    process_subject(str(sys.argv[1]))
