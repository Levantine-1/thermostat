# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file to the working directory
COPY backend/src/requirements.txt /app

# Install the dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the current directory contents into the container at /app
COPY backend/src /app

# Expose port 5005
EXPOSE 5005

# Run the command to start the app
CMD ["gunicorn", "thermostat_api_server:app", "-b", "0.0.0.0:5005"]