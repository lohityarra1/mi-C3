# Time Difference Calculator API

This API service calculates the absolute time difference between two timestamps in different time zones, as described in Task A.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn

## Installation

1. Install the required packages:

```bash
pip install fastapi uvicorn
```

2. Run the server:

```bash
python app.py
```

The server will start at http://localhost:8000

## Usage

### API Endpoints

#### POST /calculate

Calculates the time difference based on the input text.

**Request Body:**

```json
{
  "input_text": "2\nSun 10 May 2015 13:54:36 -0700\nSun 10 May 2015 13:54:36 -0000\nSat 02 May 2015 19:54:36 +0530\nFri 01 May 2015 13:54:36 -0000"
}
```

**Response:**

```json
["25200", "88200"]
```

### Example using curl

```bash
curl -X POST "http://localhost:8000/calculate" \
     -H "Content-Type: application/json" \
     -d '{"input_text": "2\nSun 10 May 2015 13:54:36 -0700\nSun 10 May 2015 13:54:36 -0000\nSat 02 May 2015 19:54:36 +0530\nFri 01 May 2015 13:54:36 -0000"}'
```

### Example using Python requests

```python
import requests

url = "http://localhost:8000/calculate"
payload = {
    "input_text": "2\nSun 10 May 2015 13:54:36 -0700\nSun 10 May 2015 13:54:36 -0000\nSat 02 May 2015 19:54:36 +0530\nFri 01 May 2015 13:54:36 -0000"
}

response = requests.post(url, json=payload)
print(response.json())
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc