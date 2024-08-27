# Use the official Playwright Docker image
FROM mcr.microsoft.com/playwright/python:v1.46.0-amd64

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

# Mount a volume for the report directory
VOLUME /app/reports

# Run main.py when the container launches
CMD ["python", "scripts/main.py"]