from datetime import datetime
import sys

def time_difference(t1, t2):
    """Calculate the absolute difference in seconds between two timestamps."""
    # Define the format of the input timestamp
    time_format = "%a %d %b %Y %H:%M:%S %z"
    
    # Parse the timestamps
    dt1 = datetime.strptime(t1, time_format)
    dt2 = datetime.strptime(t2, time_format)
    
    # Calculate the difference in seconds
    diff_seconds = int(abs((dt1 - dt2).total_seconds()))
    
    return diff_seconds

def main():
    # Read the number of test cases
    t = int(input().strip())
    
    results = []
    for _ in range(t):
        # Read the two timestamps
        timestamp1 = input().strip()
        timestamp2 = input().strip()
        
        # Calculate and print the time difference
        diff = time_difference(timestamp1, timestamp2)
        results.append(str(diff))
        print(diff)
    
    return results

if __name__ == "__main__":
    main()