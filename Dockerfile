# Docker multi-stage build for FastAPI AI Academic Research Agent
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-requires \
    build-essential \
    libgobject-2.0-0 \
    pango1.0-tools \
    fontconfig \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
