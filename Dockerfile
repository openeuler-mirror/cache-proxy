# Use an official Python runtime as a parent image
FROM cache-proxy-image:latest

WORKDIR /cache-proxy

# Add the current directory contents into the container at /cache-proxy
ADD . /cache-proxy

# Install any needed packages specified in requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000
RUN mkdir -p /tmp/cache

# Run main.py when the container launches
ENTRYPOINT python3 app/main.py