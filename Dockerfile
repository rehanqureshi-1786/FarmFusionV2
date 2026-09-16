FROM python:3.11-slim

WORKDIR /app

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal system dependencies without pulling in recommended GUI/desktop libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Install CPU-only PyTorch first to avoid downloading 4GB+ of CUDA/Triton binaries
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install remaining dependencies
COPY backend/requirements.txt ./requirements.txt
RUN sed -i '/torch/d' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source into container
COPY backend/ .
RUN mkdir -p uploads

ENV PORT=8000
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["sh", "-c", "python run.py"]
