# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Set the working directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy requirements.txt before other files to leverage Docker cache
COPY requirements.txt ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.enableCORS", "false"]
