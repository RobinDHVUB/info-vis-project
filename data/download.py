import openneuro

if __name__ == '__main__':

    # ! Expects info-visa-data/raw to exist
    
    # Download raw data (+- 85GB)
    openneuro.download(dataset="ds000117", target_dir="/scratch/brussel/102/vsc10248/info-vis-data/raw")
