FROM python:3.9-alpine


# Add security updates
RUN apk update && apk upgrade

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Generate a unique node ID at build time
ARG NODE_ID=node-unknown
ENV NODE_ID=${NODE_ID}

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]