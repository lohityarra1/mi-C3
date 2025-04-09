from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI(title="Time Difference Calculator API")

class TimeRequest(BaseModel):
    input_text: str

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

def process_input(input_text):
    """Process the input text and calculate time differences."""
    lines = input_text.strip().split('\n')
    
    try:
        t = int(lines[0])
        results = []
        
        line_index = 1
        for _ in range(t):
            if line_index + 1 >= len(lines):
                raise ValueError("Not enough timestamps provided")
                
            timestamp1 = lines[line_index]
            timestamp2 = lines[line_index + 1]
            
            diff = time_difference(timestamp1, timestamp2)
            results.append(str(diff))
            
            line_index += 2
            
        return results
    except Exception as e:
        raise ValueError(f"Error processing input: {str(e)}")

@app.post("/calculate", response_model=list[str])
async def calculate_time_difference(request: TimeRequest):
    try:
        results = process_input(request.input_text)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)