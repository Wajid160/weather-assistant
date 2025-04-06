    # Use an official Python runtime as a parent image
    FROM python:3.9-slim

    # Set the working directory in the container
    WORKDIR /app

    # Prevent Python from writing pyc files to disc or buffer stdout/stderr
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    # Install system dependencies that might be needed by some Python packages
    # (Optional, but can prevent issues)
    # RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

    # Install pip requirements
    # Copy only requirements first to leverage Docker cache
    COPY requirements.txt requirements.txt
    RUN pip install --no-cache-dir --upgrade pip
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the rest of the application code
    COPY . .

    # Make port 7860 available to the world outside this container
    # Hugging Face Spaces expects apps to run on this port by default for Docker
    EXPOSE 7860

    # Define environment variable (though HF secrets are preferred)
    # ENV CHAINLIT_PORT=7860 # Not strictly needed if EXPOSE is used

    # Run chainlit when the container launches
    # Use 0.0.0.0 to bind to all network interfaces within the container
    # -w flag enables auto-reload, useful for development but optional for production
    CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "7860"]