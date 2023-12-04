FROM python:3.11-slim-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Copy the rest of the application code to the container
COPY . .

# Set environment variables
ENV FLASK_DEBUG=1
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credenciales.json
ENV MNT_DIR=/app/uploads
ENV BUCKET=misw4204-202315-grupo21

# Install the dependencies
RUN set -e; \
    apt-get update -y && apt-get install -y \
    tini \
    curl
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.asc] https://packages.cloud.google.com/apt gcsfuse-bookworm main" | tee /etc/apt/sources.list.d/gcsfuse.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | tee /usr/share/keyrings/cloud.google.asc
RUN apt-get update
RUN apt-get install -y fuse gcsfuse
# RUN echo "misw4204-202315-grupo21  /app/uploads gcsfuse rw,_netdev,user,allow_other,gid=0,uid=0" | tee /etc/fstab
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Expose port 5000 for the Flask development server to listen on
EXPOSE 8000

# Ensure the script is executable
RUN chmod +x /app/app_run.sh

# Use tini to manage zombie processes and signal forwarding
# https://github.com/krallin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

# Pass the startup script as arguments to Tini
CMD ["/app/app_run.sh"]