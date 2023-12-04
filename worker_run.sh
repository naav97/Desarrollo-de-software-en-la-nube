#!/usr/bin/env bash
set -eo pipefail


echo "Mounting GCS Fuse."
gcsfuse --foreground --debug_gcs --debug_fuse $BUCKET $MNT_DIR &
echo "Mounting completed."

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 0 worker:app