# Backend Dockerfile
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Expose the backend port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
