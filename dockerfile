# Use an official Python runtime as a parent image
FROM python:slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the parent directory contents into the container at /app
ADD . /app

# Create .preferences file as blank json
RUN echo "{}" > .preferences

# Install build essentials for gcc, required for buidling some of the following python requirements
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential

# Install any needed packages specified in requirements.txt
RUN pip install .


# Run a shell upon starting up and keep it running
CMD tail -f /dev/null

