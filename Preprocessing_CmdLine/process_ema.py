import pandas as pd
import numpy as np
import os
import sys

# Function to remove duplicates conditionally
def Rem_Dup(df, clm):
    if df[clm].duplicated().any():
        non_numeric_values = df[~df[clm].astype(str).str.isdigit()].index
        num_dup = len(non_numeric_values)
        for i in range(num_dup):
            dup_row = non_numeric_values[i]
            content = df[clm].iloc[dup_row]
            df[clm].iloc[dup_row] = content[0]
    return

def convert_column_to_unix_utc_inplace(df, column_name):
    """Converts a column of timestamps to Unix timestamps in UTC in-place."""
    if not pd.api.types.is_datetime64_any_dtype(df[column_name]):
        print(f"Converting column '{column_name}' to datetime.")
        df[column_name] = pd.to_datetime(df[column_name], utc=True)
    else:
        print(f"Column '{column_name}' is already in datetime format.")
    
    # Print a sample of the converted column before and after conversion
    print(f"Sample of '{column_name}' before conversion to Unix timestamps:")
    print(df[column_name].head())
    
    df[column_name] = df[column_name].dt.tz_convert('UTC').astype('int64') // 1000000000
    
    print(f"Sample of '{column_name}' after conversion to Unix timestamps:")
    print(df[column_name].head())

def process_ema(ema_file_path, output_file):
    if os.path.exists(output_file):
        print(f"Loading existing file: {output_file}")
        return pd.read_csv(output_file)
    else:
        print(f"Processing EMA data and saving to {output_file}")
        
        # LOAD EMA Data
        EMA_df = pd.read_csv(ema_file_path)
        
        ## Unordered ##
        EMA_df['session_id'] = pd.Categorical(EMA_df['session_id'])
        EMA_df['ppt_id'] = pd.Categorical(EMA_df['ppt_id'])
        EMA_df['survey_name'] = pd.Categorical(EMA_df['survey_name'])

        ## Ordered ##
        for col in [
            'day_affect_stress_financial', 'day_affect_stress_friends', 'day_affect_stress_health', 
            'day_affect_stress_legal', 'day_affect_stress_overall', 'day_affect_stress_romantic', 
            'day_affect_stress_school_work', 'now_affect_agitated', 'now_affect_angry', 'now_affect_burdensome',
            'now_affect_desire_approach', 'now_affect_desire_avoid', 'now_affect_desire_escape', 
            'now_affect_energetic', 'now_affect_fatigued', 'now_affect_happy', 'now_affect_hopeless', 
            'now_affect_humiliated', 'now_affect_impulsive', 'now_affect_isolated', 'now_affect_negative', 
            'now_affect_numb', 'now_affect_overwhelmed', 'now_affect_positive', 'now_affect_relaxed', 
            'now_affect_sad', 'now_affect_self_hate', 'now_affect_stress_overall', 'now_affect_stressed', 
            'now_affect_tense', 'now_affect_trapped', 'now_affect_worried'
        ]:
            Rem_Dup(EMA_df, col)
            EMA_df = EMA_df.astype({col: int})
        
        ## Date/Time ##
        convert_column_to_unix_utc_inplace(EMA_df, 'started_at')
        EMA_df['started_at'] = EMA_df['started_at'].astype(np.int64)
        EMA_df = EMA_df[~EMA_df.index.duplicated(keep='first')]  # Remove duplicates if they exist
        
        # Check if 999 exists in the DataFrame
        if (EMA_df == 999).any().any():
            EMA_df = EMA_df.replace(999, np.nan)  # Replace 999 with NaN

        # Check if 888 exists in the DataFrame
        if (EMA_df == 888).any().any():
            EMA_df = EMA_df.replace(888, np.nan)  # Replace 888 with NaN
        
        EMA_df.to_csv(output_file, index=False)
        return EMA_df

def run(ema_file_path):
    output_file = './EMA_Processed.csv'

    process_ema(ema_file_path, output_file)
