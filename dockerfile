# # Start with a base image that has Python
# FROM python:3.11-slim

# # Set up environment variables
# ENV PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1

# # Set the working directory in the container
# WORKDIR /app

# # Copy requirements file and install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the application files
# COPY . .

# # Expose the port FastAPI will run on
# EXPOSE 8000

# # Start Uvicorn with the main FastAPI app
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



# Start with a base image that has Python
FROM python:3.11-slim

# Set up environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install Supervisor
RUN apt-get update && apt-get install -y supervisor

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Add Supervisor config file to Docker container
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start Supervisor as the entry point
CMD ["/usr/bin/supervisord"]
