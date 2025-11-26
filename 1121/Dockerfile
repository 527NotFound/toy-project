# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the HTML file into the container
COPY prompt_ui.html .

# Install a simple HTTP server (optional, but good practice if not using Nginx)
# We will use Python's built-in http.server
# No need for extra installation as it's built-in.

# Expose the port the server will run on
EXPOSE 8000

# Command to run the simple HTTP server
CMD [ "python", "-m", "http.server", "8000" ]