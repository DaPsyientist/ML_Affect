## Import Packages ##
import sys
import numpy as np
import pickle
import pandas as pd
import glob
import os
from tqdm import tqdm

## Helper functions for preprocessing data ##
#Waveform Length of the signals (Equation)
def waveform_length(X):
    # Compute the differences between successive values
    delta_X = np.diff(X)
    
    # Square the differences and sum them
    X_wl = np.sum(delta_X**2)
    
    return X_wl


# Slope sign changes (Count)
def slope_sign_changes(X, epsilon=0.001):
    """
    Calculate the Slope Sign Changes (SSC) of a signal X.
    
    Parameters:
    X (array-like): The input signal.
    epsilon (float): The slope threshold. Default is 0.001.
    
    Returns:
    int: The number of slope sign changes in the signal.
    """
    X = X[0]
    # Initialize SSC counter
    X_ssc = 0

    # Iterate over the signal from the second element to the second-to-last element
    for K in range(1, len(X) - 2):
        # Calculate the slope sign changes
        if (np.sign(X[K] - X[K-1]) * np.sign(X[K+1] - X[K]) < 0 and
            abs(X[K] - X[K-1]) >= epsilon and abs(X[K-1] - X[K]) >= epsilon):
            X_ssc += 1

    return X_ssc


# Willison amplitude (equation)
def willison_amplitude(X, epsilon_W=0.01):
    """
    Calculate the Willison Amplitude (WAMP) of a signal X.
    
    Parameters:
    X (array-like): The input signal.
    epsilon_W (float): The Willison threshold. Default is 0.5.
    
    Returns:
    int: The Willison Amplitude of the signal.
    """
    
    # Initialize WAMP counter
    X_wamp = 0

    # Iterate over the signal from the second element to the last element
    for K in range(1, len(X)):
        # Check if the absolute difference exceeds the threshold epsilon_W
        if abs(X[K] - X[K-1]) >= epsilon_W:
            X_wamp += 1

    return X_wamp


# Split participants EDA data into distinct sessions preceding EMA ratings
def split_sessions(df, time_gap=600000):
    # Ensure data is sorted by the timestamp
    df = df.sort_values('Unix Timestamp (UTC)')
    
    # Calculate the difference between consecutive timestamps
    df['time_diff'] = df['Unix Timestamp (UTC)'].diff().fillna(0)
    
    # Identify session breaks (where the time difference exceeds the time gap)
    session_starts = df['time_diff'] > time_gap
    
    # Create a session number column
    df['session_num'] = session_starts.cumsum() + 1
    
    # Extract participant ID from the DataFrame
    ppt_id = df['ppt_id'].iloc[0]
    
    # Split the data by session and save to new files in the current working directory
    for session, session_data in df.groupby('session_num'):
        session_file = f'{ppt_id}_S{session}.csv'
        session_data.drop(columns=['time_diff', 'session_num'], inplace=True)
        session_data.to_csv(session_file, index=False)
        print(f'Session {session} saved to {session_file}')

## Code to preprocess data for each participant ##
# File to store the EDA data
output_file = 'eda_data_list.pkl'

#List the files specified in the command line
inputFiles = sys.argv[1:] 

# Process each participant from command-line arguments
for participant in inputFiles:
    # Load each participant's EDA signal data
    eda_df = pd.read_csv(f"{participant}_EDA.csv")
    # Split up each participants data based on the number of sessions available
    split_sessions(eda_df)
    # Create lowercase version of the participant ID
    participant_lower = participant.lower()

    # Define patterns to match files for this participant
    patterns = [
        f'u01-{participant_lower}_S[1-9].csv',          # Match S1 to S9
        f'u01-{participant_lower}_S[1-9][0-9].csv',     # Match S10 to S99
        f'u01-{participant_lower}_S1[0-9][0-9].csv',    # Match S100 to S199
        ]

    # Use glob to find all files matching the patterns
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
        for file in files:
            # Load the CSV file into a DataFrame
            df = pd.read_csv(file)
            print(f"Loaded data for participant: {participant_lower} from file: {file}")
            
            # Extract session info from the filename
            session_num = file.split('_')[-1].split('.')[0]  # Pullo out word after '_' and before '.csv' (S[###])

            # Pull out raw Galvanic Skin Response (GSR) data
            eda_signal = df['EDA (microS)'].values
            
            # Determine amount of EDA data present in each session
            amt_trls = len(eda_signal)/4
            
            # Set the parameter in PyEDA
            Seg_w = int(amt_trls//4) #4 hertz per second, rounded to closest integer value for setting parameter value
            
            # Calculate the difference between the width and amount of trials
            leftover_trials = len(eda_signal) - (Seg_w * 4)
            
            # If there are leftover trials to drop, alter the DataFrame
            if leftover_trials > 0:
                # Drop the first `leftover_trials` rows
                eda_signal = eda_signal[leftover_trials:]  # Adjust the DataFrame

            #Automatically preprocess EDA signal using PyEDA
            m, wd, eda_clean = process_statistical(eda_signal, use_scipy=True, sample_rate=4, segment_width=Seg_w, segment_overlap=0)

            ## Calculate statistical EDA metrics ##
            # Based on 33 metrics from Petrescu et al., 2021: 
            # - 6 metrics (no baseline measurement of EDA)
            # - 9 metrics (not a high enough frequency for power analysis)
            # 18 total metrics

            ## Event-related features (provided by PyEDA) (3) ##
            # Average amplitude of GSR
            GSR_avimp = m['mean_gsr'][0]
            # Number of electrodermal responses
            GSR_nimp = m['number_of_peaks'][0]
            # Maximum amplitude of GSR
            GSR_maximp = m['max_of_peaks'][0]

            ## Time-related features (provided by PyEDA) (12) ##
            # Mean Absolute values of signals (3) #
            # Galvinic Skin Response
            GSR_mav = np.mean(np.abs(eda_clean))
            # Skin Conductance Level
            SCL_mav = np.mean(np.abs(wd['tonic_gsr']))
            # Skin Conductance Response
            SCR_mav = np.mean(np.abs(wd['filtered_phasic_gsr']))

            # Standard Deviation of signals (3) #
            # Galvinic Skin Response
            GSR_std = np.std(eda_clean)
            # Skin Conductance Level
            SCL_std = np.std(wd['tonic_gsr'])
            # Skin Conductance Response
            SCR_std = np.std(wd['filtered_phasic_gsr'])

            # Slope sign changes of the signal (3) #
            # Galvinic Skin Response
            GSR_ssc = slope_sign_changes(eda_clean)
            # Skin Conductance Level
            SCL_ssc = slope_sign_changes(wd['tonic_gsr'])
            # Skin Conductance Response
            SCR_ssc = slope_sign_changes(wd['filtered_phasic_gsr'])

            ## Waveform Length of the signals (3) ##
            # Galvinic Skin Response
            GSR_wl = waveform_length(eda_clean)
            # Skin Conductance Level
            SCL_wl = waveform_length(wd['tonic_gsr'])
            # Skin Conductance Response
            SCR_wl = waveform_length(wd['filtered_phasic_gsr'])

            ## Willison Amplitude of the signals (3) ##
            # Galvinic Skin Response
            GSR_wamp = willison_amplitude(eda_clean)
            # Skin Conductance Level
            SCL_wamp = willison_amplitude(wd['tonic_gsr'])
            # Skin Conductance Response
            SCR_wamp = willison_amplitude(wd['filtered_phasic_gsr'])

            # Create entry for participant and EDA data
            participant_data = {"participant": participant, "session": session_num, "eda": eda_signal, "GSR_avimp": GSR_avimp, "GSR_nimp":GSR_nimp, "GSR_maximp":GSR_maximp, "GSR_mav":GSR_mav, "SCL_mav":SCL_mav, "SCR_mav":SCR_mav, "GSR_std":GSR_std, "SCL_std":SCL_std, "SCR_std":SCR_std, "GSR_ssc":GSR_ssc, "SCL_ssc":SCL_ssc, "SCR_ssc":SCR_ssc, "GSR_wl":GSR_wl, "SCL_wl":SCL_wl, "SCR_wl":SCR_wl, "GSR_wamp":GSR_wamp, "SCL_wamp":SCL_wamp, "SCR_wamp":SCR_wamp}
            
            # Append to the file after processing each participant
            with open(output_file, 'ab') as f:  # 'ab' mode for appending binary data
                pickle.dump(participant_data, f)

    print(f"Appended data for participant: {participant}")
print("All done!")