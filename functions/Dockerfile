# Use Python 3.11 as base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    python3-dev \
    cmake \
    libcairo2-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy function code, requirements, and models
COPY . .

# Create the models directory in the expected location
RUN mkdir -p /root/.chess_diagram_to_fen/storages

# Copy models to the correct location
RUN cp -r models/* /root/.chess_diagram_to_fen/storages/

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV FUNCTION_TARGET=process_chess_image
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port 8080
EXPOSE 8080

# Use Functions Framework to start the function with the correct port
CMD exec functions-framework --target=${FUNCTION_TARGET} --port=${PORT} --debug