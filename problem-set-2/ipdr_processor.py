import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def process_ipdr_data(file_path):
    """
    Process IPDR data to calculate audio and video call metrics based on the given requirements.
    
    Args:
        file_path: Path to the Excel file containing IPDR data
        
    Returns:
        DataFrame with processed call data
    """
    # Load the data
    df = pd.read_excel(file_path)
    
    # Ensure required columns exist
    required_columns = ['MSISDN', 'Domain name', 'Start DateTime', 'End DateTime', 'Upload Volume', 'Download Volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in the data")
    
    # Rename columns for easier processing
    df = df.rename(columns={
        'Domain name': 'DOMAIN',
        'Start DateTime': 'START_TIME',
        'End DateTime': 'END_TIME',
        'Upload Volume': 'UL_VOLUME',
        'Download Volume': 'DL_VOLUME'
    })
    
    # Convert time columns to datetime
    df['START_TIME'] = pd.to_datetime(df['START_TIME'])
    df['END_TIME'] = pd.to_datetime(df['END_TIME'])
    
    # Ensure volume columns are numeric (they are in bytes)
    df['UL_VOLUME'] = pd.to_numeric(df['UL_VOLUME'], errors='coerce').fillna(0)
    df['DL_VOLUME'] = pd.to_numeric(df['DL_VOLUME'], errors='coerce').fillna(0)
    
    # Group by MSISDN and domain (app)
    result_rows = []
    
    # Process each MSISDN and domain combination
    for (msisdn, domain), group_df in df.groupby(['MSISDN', 'DOMAIN']):
        # Sort by start time
        group_df = group_df.sort_values('START_TIME')
        
        # Identify individual calls with gap detection
        calls = []
        current_call = [group_df.iloc[0]]
        
        for i in range(1, len(group_df)):
            current_row = group_df.iloc[i]
            previous_row = group_df.iloc[i-1]
            
            # If this record starts after the previous one ends, consider it part of the same call
            # Otherwise, it's a new call
            if current_row['START_TIME'] <= previous_row['END_TIME'] + timedelta(minutes=10):
                current_call.append(current_row)
            else:
                calls.append(current_call)
                current_call = [current_row]
                
        # Add the last call
        if current_call:
            calls.append(current_call)
        
        # Process each call
        for call_records in calls:
            call_df = pd.DataFrame(call_records)
            
            # Apply the idle time exclusion logic
            adjusted_call_df = adjust_end_times(call_df)
            
            # Calculate metrics for this call
            call_metrics = calculate_call_metrics(adjusted_call_df, msisdn, domain)
            
            if call_metrics:
                result_rows.append(call_metrics)
    
    # Create the result DataFrame
    result_df = pd.DataFrame(result_rows)
    
    # Filter out calls with bitrate < 10 kbps
    if not result_df.empty:
        result_df = result_df[result_df['kbps'] >= 10]
    
    return result_df

def adjust_end_times(call_df):
    """
    Adjust end times to exclude idle periods (10 minutes).
    
    For each FDR:
    - Calculate ET* (ET - 10 min)
    - If ET* < ST, keep the original ET
    
    Args:
        call_df: DataFrame containing records for a single call
        
    Returns:
        DataFrame with adjusted end times
    """
    # Make a copy to avoid modifying the original
    adjusted_df = call_df.copy()
    
    # For each FDR, calculate ET* (ET - 10 min)
    adjusted_df['ET_STAR'] = adjusted_df['END_TIME'] - timedelta(minutes=10)
    
    # If ET* < ST, keep the original ET
    adjusted_df['ADJUSTED_END_TIME'] = adjusted_df.apply(
        lambda row: row['END_TIME'] if row['ET_STAR'] < row['START_TIME'] else row['ET_STAR'],
        axis=1
    )
    
    return adjusted_df

def calculate_call_metrics(call_df, msisdn, domain):
    """
    Calculate metrics for a single call.
    
    Args:
        call_df: DataFrame containing records for a single call
        msisdn: The MSISDN (phone number)
        domain: The app/domain name
        
    Returns:
        Dictionary with call metrics
    """
    # Calculate total volume in Kb (converting from Bytes)
    total_ul_volume = call_df['UL_VOLUME'].sum() / 1024  # Bytes to Kb
    total_dl_volume = call_df['DL_VOLUME'].sum() / 1024  # Bytes to Kb
    total_volume = total_ul_volume + total_dl_volume
    
    # Calculate total duration in seconds
    min_start_time = call_df['START_TIME'].min()
    max_end_time = call_df['ADJUSTED_END_TIME'].max()
    duration_sec = (max_end_time - min_start_time).total_seconds()
    
    # Avoid division by zero
    if duration_sec <= 0:
        return None
    
    # Calculate bit rate in kbps (kilobits per second)
    # 1 Kilobyte = 8 Kilobits
    kbps = (total_volume * 8) / duration_sec
    
    # Determine if it's an audio or video call
    is_audio = 1 if kbps <= 200 else 0
    is_video = 1 if kbps > 200 else 0
    
    return {
        'msisdn': msisdn,
        'domain': domain,
        'durations_sec': int(duration_sec),
        'fdr_count': len(call_df),
        'kbps': round(kbps, 2),
        'isAudio': is_audio,
        'isVideo': is_video
    }

def main():
    # File path to the IPDR data (Excel sheet)
    file_path = 'ipdr_data.xlsx'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found. Please download the IPDR data and save it as '{file_path}'.")
        return
    
    # Process the data
    result_df = process_ipdr_data(file_path)
    
    if result_df.empty:
        print("No valid call records found after processing.")
        return
    
    # Save the results
    result_df.to_csv('ipdr_call_analysis.csv', index=False)
    print(f"Analysis complete. Results saved to 'ipdr_call_analysis.csv'")
    
    # Print summary statistics
    total_calls = len(result_df)
    audio_calls = result_df['isAudio'].sum()
    video_calls = result_df['isVideo'].sum()
    
    print(f"Total calls analyzed: {total_calls}")
    print(f"Audio calls: {audio_calls}")
    print(f"Video calls: {video_calls}")
    
    # Group by domain and count call types
    domain_summary = result_df.groupby('domain').agg({
        'isAudio': 'sum',
        'isVideo': 'sum',
        'durations_sec': 'sum'
    }).reset_index()
    
    domain_summary['total_calls'] = domain_summary['isAudio'] + domain_summary['isVideo']
    domain_summary['avg_duration_sec'] = domain_summary['durations_sec'] / domain_summary['total_calls']
    
    print("\nCalls by domain:")
    print(domain_summary)

if __name__ == "__main__":
    main()