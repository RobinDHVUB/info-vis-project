import mne
import os
from mne_bids import BIDSPath, read_raw_bids

bids_path = BIDSPath(root="data/raw", datatype="eeg")

# Read raw
raw = read_raw_bids(bids_path)
print(raw.info['subject_info'])