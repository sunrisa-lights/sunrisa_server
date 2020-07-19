# Use the official image as a parent image.
FROM python:3.8.1-slim-buster

# Set the working directory.
WORKDIR /usr/src/sunrisa/sunrisa_server

# Copy the file from Dockerfile location to WORKDIR
COPY requirements.txt .
COPY app_config.py .
COPY sunrisa.py .
COPY app ./app
COPY healthcheck.py .

# install make
RUN apt-get update && apt-get install make

# Run the command inside your image filesystem.
RUN pip install --upgrade -r requirements.txt

# Add metadata to the image to describe which port the container is listening on at runtime.
EXPOSE 5000

# Run the specified command within the container. Use -u so that stdout is unbuffered.
CMD [ "python", "-u", "sunrisa.py" ]

HEALTHCHECK --interval=5m --timeout=3s \
  CMD python healthcheck.py
