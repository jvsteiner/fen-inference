# Use Python 3.10 as base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    python3-dev \
    cmake \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy function code and requirements
COPY . .

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install pyfastnoisesimd first
RUN pip install --no-cache-dir pyfastnoisesimd==0.4.2

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the function to be executed
ENV FUNCTION_TARGET=process_chess_image

# Expose port 8080
EXPOSE 8080

# Use Functions Framework to start the function
CMD ["functions-framework", "--target", "process_chess_image"] 