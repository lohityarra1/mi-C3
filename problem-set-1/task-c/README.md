# Containerized Time Difference Calculator

This is a containerized version of the Time Difference Calculator API that runs multiple instances with load balancing.

## Requirements

- Docker
- Docker Compose

## Architecture

The application consists of:
- Two API service instances (app1 and app2) with unique node IDs
- Nginx as a load balancer
- Each service returns its node ID in the response

## Running the Application

1. Make sure Docker and Docker Compose are installed on your system.

2. Build and start the containers:

```bash
docker-compose up -d
```

3. The service will be available at http://localhost:8000

4. To stop the service:

```bash
docker-compose down
```

## API Usage

### POST /calculate

Calculates the time difference based on the input text, and includes the ID of the node that processed the request.

**Request Body:**

```json
{
  "input_text": "2\nSun 10 May 2015 13:54:36 -0700\nSun 10 May 2015 13:54:36 -0000\nSat 02 May 2015 19:54:36 +0530\nFri 01 May 2015 13:54:36 -0000"
}
```

**Response:**

```json
{
  "id": "node-1",
  "result": ["25200", "88200"]
}
```

### Example using curl

```bash
curl -X POST "http://localhost:8000/calculate" \
     -H "Content-Type: application/json" \
     -d '{"input_text": "2\nSun 10 May 2015 13:54:36 -0700\nSun 10 May 2015 13:54:36 -0000\nSat 02 May 2015 19:54:36 +0530\nFri 01 May 2015 13:54:36 -0000"}'
```

## Testing Load Balancing

You can make multiple requests to see different node IDs in the response, showing that the load balancer is distributing requests:

```bash
for i in {1..10}; do 
  curl -X POST "http://localhost:8000/calculate" \
       -H "Content-Type: application/json" \
       -d '{"input_text": "1\nSun 10 May 2015 13:54:36 -0700\nSun 10 May 2015 13:54:36 -0000"}' | jq .id
done
```

## Scaling the Application

To add more instances, you can update the `docker-compose.yml` file to include additional services with unique node IDs.

## Direct Access to Individual Nodes

You can also access each node directly for testing:
- Node 1: http://localhost:8001
- Node 2: http://localhost:8002