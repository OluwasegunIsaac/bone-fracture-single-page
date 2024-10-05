# Use the official lightweight Python image.
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Set the working directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install system dependencies for OpenCV and others
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt before other files to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.enableCORS", "false"]
