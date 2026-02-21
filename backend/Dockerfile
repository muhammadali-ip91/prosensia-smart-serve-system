FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
	gcc \
	libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ./backend/

# Copy AI module (needed for ETA prediction)
COPY ../ai_module ./ai_module/

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "backend.main:socket_app", "--host", "0.0.0.0", "--port", "8000"]

