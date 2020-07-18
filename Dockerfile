# Use the official image as a parent image.
FROM python:3.6.5

# Set the working directory.
WORKDIR /home/ubuntu/sunrisa_server

# Copy the file from your host to your current location.
COPY requirements.txt .

# Run the command inside your image filesystem.
RUN pip install -r requirements.txt

# Add metadata to the image to describe which port the container is listening on at runtime.
EXPOSE 3000

# Run the specified command within the container.
CMD [ "make", "run" ]

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . .

