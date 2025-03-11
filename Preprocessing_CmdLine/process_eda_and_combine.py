import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob
import sys
from tqdm import tqdm

# Function to mark overlaps
def mark_overlaps(df1, col1, df2, col2, interval_minutes, chunk_size=1000000):
    interval_seconds = interval_minutes * 60
    df1['time_ts'] = df1['Unix Timestamp (UTC)'].astype(np.int64) // 1000  # Convert to seconds
    df2['overlap'] = False
    
    # Create a new DataFrame to store the filtered data
    filtered_data = pd.DataFrame()

    # Process df1 in chunks
    num_chunks = (len(df1) + chunk_size - 1) // chunk_size
    for i in tqdm(range(num_chunks), desc="Processing chunks"):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(df1))
        chunk_df1 = df1.iloc[start_idx:end_idx]

        for idx, row in df2.iterrows():
            start_time = row['started_at']
            start_interval = start_time - interval_seconds
            interval_data = chunk_df1[(chunk_df1['time_ts'] >= start_interval) & (chunk_df1['time_ts'] < start_time)]
            
            if not interval_data.empty:
                df2.at[idx, 'overlap'] = True
                filtered_data = pd.concat([filtered_data, interval_data], ignore_index=True)

    return filtered_data, df2

def process_or_load(df1, col1, df2, col2, output_EMA, output_EDA, participant_id_ema_format, interval_minutes=10, chunk_size=1000000):
    if os.path.exists(output_EMA):
        print(f"Loading existing file: {output_EMA}")
    else:
        print(f"File not found. Running mark_overlaps and saving to {output_EMA}")
        df2_filtered = df2[df2['ppt_id'] == participant_id_ema_format]
        result_df1, result_df2 = mark_overlaps(df1, col1, df2_filtered, col2, interval_minutes)
        result_df1.to_csv(output_EDA, index=False)
        result_df2.to_csv(output_EMA, index=False)

def process_eda_and_combine(user_id, ema_file_path):
    output_EMA = f'./{user_id}_overlaps.csv'
    output_EDA = f'./{user_id}_EDA.csv'
    EMA_df = pd.read_csv(ema_file_path)
    file_pattern = f'*_{user_id}_*.csv'
    files = glob.glob(file_pattern)

    if not files:
        print(f"No files found for User ID {user_id}")
        return

    user_id_lower = user_id.lower()
    user_map = EMA_df[EMA_df['ppt_id'].str.contains(user_id_lower, case=False)].iloc[0]
    prefix = user_map['ppt_id'].split('-')[0]
    participant_id_ema_format = f'{prefix}-{user_id_lower}'

    for file in files:
        EDA_df = pd.read_csv(file)
        EDA_df['ppt_id'] = participant_id_ema_format
        process_or_load(EDA_df, 'Unix Timestamp (UTC)', EMA_df, 'started_at', output_EMA, output_EDA, participant_id_ema_format, interval_minutes=10)

def run(user_id):
    ema_file_path = './EMA_Processed.csv'
    process_eda_and_combine(user_id, ema_file_path)