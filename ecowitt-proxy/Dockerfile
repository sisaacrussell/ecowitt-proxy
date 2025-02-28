FROM python:3.12-alpine

# Install dependencies
RUN apk --update --no-cache add python3 py3-pip

# Install required Python packages
RUN pip install --no-cache-dir requests flask

# Create working directory
RUN mkdir /app

# Copy application files
COPY app/ /app
RUN chmod +x /app/run.sh

# Set working directory
WORKDIR /app

# Run script
CMD ["./run.sh"]
