# Use an official Python runtime as a parent image
FROM cache-proxy-image:latest

WORKDIR /cache-proxy

# Add the current directory contents into the container at /cache-proxy
ADD . /cache-proxy

# Install any needed packages specified in requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000
RUN mkdir -p /tmp/cache
RUN yum install -y findutils
RUN pip freeze | cut -d = -f 1 | xargs pip install -U -i https://pypi.tuna.tsinghua.edu.cn/simple

# Run main.py when the container launches
ENTRYPOINT python3 app/main.py