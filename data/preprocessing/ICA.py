import mne
import os
from mne.preprocessing import ICA

# Create ICA-processed folder
if os.path.isdir("data/ICA_processed"):
    print("ICA_processed folder exists, clear first")
    quit()
else:
    os.mkdir("data/ICA_processed")

# Log file
with open('data/ICA_processed/excluded_comps.txt', 'w') as f:

    # Loop over subjects
    for subject_folder in os.listdir("data/processed"):

        # Make folder for subject ICA-processed
        os.mkdir("data/ICA_processed/" + subject_folder)

        # Loop over runs
        for run_id, run_file in enumerate(os.listdir("data/processed/" + subject_folder)):

            # Read raw
            raw = mne.io.read_raw_fif("data/processed/" + subject_folder + "/" + run_file)

            ica = ICA(n_components=20, max_iter='auto', random_state=97)
            ica.fit(raw)

            # Plotting components
            raw.load_data()
            ica.plot_sources(raw, show_scrollbars=True, block=True)


            # Ask for components to exclude
            string_input = input("Components to exclude (comma separated): ")
            to_exclude = [int(comp) for comp in string_input.split(",")]

            # Plotting reconstructions if needed
            ica.plot_overlay(raw, exclude=to_exclude, picks='eeg')
            ica.plot_overlay(raw, exclude=to_exclude, picks='mag')

            # Applying repair
            ica.exclude = to_exclude
            ica.apply(raw)

            # Saving ICA-processed run
            raw.save("data/ICA_processed/" + subject_folder + "/" + run_file)

            # Write excluded comps
            f.write(subject_folder + ", " + run_file + ", [" + string_input + "]\n")