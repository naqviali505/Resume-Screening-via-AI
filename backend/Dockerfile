# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend + AI agent code
COPY . .

# Expose the port Cloud Run expects
EXPOSE 8080

# Run FastAPI
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
