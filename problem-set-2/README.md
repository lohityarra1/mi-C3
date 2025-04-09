# IPDR Data Processing for Audio/Video Call Analysis

This solution processes Internet Protocol Detail Record (IPDR) data to analyze VoIP application usage, distinguishing between audio and video calls based on bitrate.

## Architecture

The solution follows a data pipeline architecture:

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌─────────────┐
│ IPDR Data   │ → │ Data Loading  │ → │ Call Detection │ → │ Metric      │
│ (Excel)     │    │ & Preprocessing│    │ & Processing   │    │ Calculation │
└─────────────┘    └──────────────┘    └────────────────┘    └─────────────┘
                                                                     │
                                                                     ▼
                                                              ┌─────────────┐
                                                              │ Results     │
                                                              │ Output      │
                                                              └─────────────┘
```

### Data Processing Workflow

```
┌─────────────────────────┐
│ Load IPDR Data from Excel│
└──────────┬──────────────┘
           │
           ▼
┌──────────────────────────┐
│ Group by MSISDN & Domain │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Sort by Start Time       │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Identify Individual Calls│
│ (Gap > 10min = New Call) │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ For Each Call:           │
└──────────┬───────────────┘
           │
┌──────────▼───────────────┐
│ Apply Idle Time Exclusion│
│ ET* = ET - 10min         │
│ If ET* < ST, keep ET     │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Calculate Total Volume   │
│ & Total Duration         │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Calculate Bitrate (kbps) │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Filter (Bitrate >= 10kbps)│
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Classify: Audio (<=200kbps)│
│ or Video (>200kbps)      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Generate Output CSV      │
└──────────────────────────┘
```

## Requirements

- Python 3.8+
- pandas
- numpy
- openpyxl (for Excel file support)

## Installation

1. Install the required packages:

```bash
pip install pandas numpy openpyxl
```

2. Place the IPDR data Excel file in the same directory as the script.

## Usage

1. Download the IPDR data from the provided Google Sheets link and save it as an Excel file named `ipdr_data.xlsx` in the same directory as the script.

2. Run the script:

```bash
python ipdr_processor.py
```

3. The script will output:
   - A CSV file `ipdr_call_analysis.csv` with the detailed results
   - Summary statistics in the console

## How It Works

The solution implements the requirements exactly as specified in the assessment:

1. **Data Loading and Preprocessing**:
   - Load the IPDR data from Excel
   - Convert time fields to datetime format
   - Ensure volume fields are numeric

2. **Call Detection**:
   - Group records by MSISDN and domain
   - Sort by start time
   - Identify individual calls based on time gaps (>10 minutes between records)

3. **Idle Time Exclusion**:
   - For each FDR, calculate ET* (ET - 10 min)
   - If ET* < ST, keep the original ET

4. **Call Metrics Calculation**:
   - Calculate total volume in Kb: Sum(DL volume + UL volume) / 1024 (converting from bytes)
   - Calculate total call time in seconds: (Max adjusted ET - Min ST)
   - Calculate bitrate in kbps: (Total volume × 8) ÷ Total time

5. **Call Classification**:
   - Filter out calls with bitrate < 10 kbps
   - Classify calls as audio (≤ 200 kbps) or video (> 200 kbps)

## Output Format

The final output contains the following columns as specified in the assessment:

- msisdn: Mobile subscriber number
- domain: VoIP application domain
- durations_sec: Call duration in seconds
- fdr_count: Number of flow data records for this call
- kbps: Calculated bitrate in kilobits per second
- isAudio: Binary flag (1=audio call, 0=not audio)
- isVideo: Binary flag (1=video call, 0=not video)

## Implementation Notes

1. **Call Detection Logic**:
   - Records are considered part of the same call if the start time of the current record is within 10 minutes of the end time of the previous record
   - Otherwise, a new call is started

2. **Idle Time Handling**:
   - For each record, we calculate ET* = ET - 10min
   - If ET* < ST, we keep the original ET to avoid negative durations

3. **Bitrate Calculation**:
   - Volume values are converted from bytes to kilobits (÷1024×8)
   - Bitrate = Total volume in kilobits ÷ Total duration in seconds

4. **Classification**:
   - Records with bitrate < 10 kbps are discarded
   - Records with 10 kbps ≤ bitrate ≤ 200 kbps are classified as audio calls
   - Records with bitrate > 200 kbps are classified as video calls

## Example Analysis Output

The script provides summary statistics showing:
- Total calls analyzed
- Number of audio and video calls
- Breakdown of calls by domain
- Average duration by domain