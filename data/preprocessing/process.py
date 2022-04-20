import mne
import sys
import os
import json
import numpy


def process_subject(subject_folder, raw_folder, processed_folder):

    # Make folder for subject
    os.mkdir(processed_folder +"/data/processed/" + subject_folder)

    # Loop over runs
    for run_id, run_file in enumerate(
        os.listdir(raw_folder + "/data/raw/" + subject_folder)
    ):

        # Make folder for run
        os.mkdir(
            processed_folder + "data/processed/"
            + subject_folder
            + "/run"
            + str(run_id)
        )

        # Read raw
        raw = mne.io.read_raw_fif(
            raw_folder + "/data/raw/" + subject_folder + "/" + run_file
        )

        # Do once
        if run_id == 0:

            # Get and save subject metadata
            # See: https://mne.tools/dev/generated/mne.Info.html
            with open(
                processed_folder + "/data/processed/" + subject_folder + "/info.json", "w"
            ) as outfile:
                json.dump(raw.info["subject_info"], outfile)

            # Get and save MEG coords and names (fixed for every run)
            meg_coords = mne.channels.find_layout(raw.info, ch_type="mag").pos
            meg_names = mne.channels.find_layout(raw.info, ch_type="mag").names
            numpy.save(
                processed_folder + "/data/processed/" + subject_folder + "/meg_coords.npy", meg_coords
            )
            numpy.save(processed_folder + "/data/processed/" + subject_folder + "/meg_names.npy", meg_names)

        # Get and save EEG coords and names (can vary per run)
        eeg_coords = mne.channels.find_layout(raw.info, ch_type="eeg").pos
        eeg_names = mne.channels.find_layout(raw.info, ch_type="eeg").names
        numpy.save(
            processed_folder + "/data/processed/"
            + subject_folder
            + "/run"
            + str(run_id)
            + "/eeg_coords.npy",
            eeg_coords,
        )
        numpy.save(
            processed_folder + "/data/processed/"
            + subject_folder
            + "/run"
            + str(run_id)
            + "/eeg_names.npy",
            eeg_names,
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
        ica.exclude = []
        eog_indices, eog_scores = ica.find_bads_eog(
            raw
        )  # Use EOG to find bad components
        ecg_indices, ecg_scores = ica.find_bads_ecg(
            raw, method="correlation", threshold="auto"
        )  # Use ECG to find bad components
        plot = ica.plot_sources(raw, stop=10, show_scrollbars=False) # Plot ICA comps for first 10 seconds
        plot.savefig(
            processed_folder + "/data/processed/"
            + subject_folder
            + "/run"
            + str(run_id)
            + "/ICA.pdf"
        )
        ica.exclude = eog_indices + ecg_indices
        ica.fit(raw)  # Apply

        # Pick MEG, EEG and stim channels
        raw.pick_types(meg="mag", eeg=True, stim=True)

        # Save
        raw.save(
            processed_folder + "/data/processed/"
            + subject_folder
            + "/run"
            + str(run_id)
            + "/processed.fif"
        )


if __name__ == "__main__":
    process_subject(*[str(arg) for arg in sys.argv])
