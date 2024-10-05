# Use the official lightweight Python image.
FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ENABLECORS=false

# Set the working directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE $STREAMLIT_SERVER_PORT

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port", "$STREAMLIT_SERVER_PORT", "--server.enableCORS", "$STREAMLIT_SERVER_ENABLECORS"]
