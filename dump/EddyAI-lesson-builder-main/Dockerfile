# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Setup venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5500 available to the world outside this container
EXPOSE 5500

# Run server when the container launches with Gunicorn and set the timeout to 10 minutes
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5500", "--timeout", "600", "wsgi:app"]
