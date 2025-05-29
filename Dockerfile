# Use the official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (for lxml, cryptography, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libxml2-dev libxslt1-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy the entire codebase
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Default command to launch your app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]