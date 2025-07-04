# Use official Python image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8001

# Start the FastAPI API (update if your main app is different)
CMD ["python", "-m", "uvicorn", "services.chat_service.api:app", "--host", "0.0.0.0", "--port", "8001"] 