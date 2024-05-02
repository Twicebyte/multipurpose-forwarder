# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

LABEL org.opencontainers.image.source=https://github.com/twicebyte/multipurpose-forwarder
LABEL org.opencontainers.image.description="Multipurpose Forwarder Image"
LABEL org.opencontainers.image.licenses=MIT

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose the port on which the Flask application will run
EXPOSE 5000

# Set the environment variable to run the Flask application in production mode
ENV FLASK_ENV=production

# Set the entry point to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
