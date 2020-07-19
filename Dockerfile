# Use the official image as a parent image.
FROM python:3.8.1-slim-buster

# Set the working directory.
WORKDIR /usr/src/sunrisa/sunrisa_server

# Copy the file from Dockerfile location to WORKDIR
COPY . .

# install make
RUN apt-get update && apt-get install make

# Run the command inside your image filesystem.
RUN pip install --upgrade -r requirements.txt

# Add metadata to the image to describe which port the container is listening on at runtime.
EXPOSE 5000

# Run the specified command within the container.
CMD [ "python", "sunrisa.py" ]

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . .
