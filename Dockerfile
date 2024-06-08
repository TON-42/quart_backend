# Dockerfile for Backend
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy project files
ADD . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "cashAndPayBot.py"]
