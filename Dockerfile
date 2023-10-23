FROM python:3.11-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Copy the rest of the application code to the container
COPY . .

RUN apk add ffmpeg

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables
ENV FLASK_DEBUG=1

# Expose port 5000 for the Flask development server to listen on
EXPOSE 5000

# Define the command to run the Flask development server
RUN chmod +x ./run.sh
CMD ./run.sh