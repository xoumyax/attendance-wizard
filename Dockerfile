FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for database
RUN mkdir -p /app/data

# Make startup script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Run startup script (seeds database + starts server)
CMD ["./start.sh"]
