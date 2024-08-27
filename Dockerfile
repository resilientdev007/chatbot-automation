# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install the SpaCy model
RUN python -m spacy download en_core_web_sm

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Mount a volume for the report directory
VOLUME /app/reports

# Run main.py when the container launches
CMD ["python", "main.py"]
