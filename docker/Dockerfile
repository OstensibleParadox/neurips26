FROM python:3.11-slim

# NOTE: Metal backend requires running on Apple Silicon natively.
# This image is for CPU-based reproducibility checks only.
# For M4 Max, run directly with llama.cpp compiled with -DLLAMA_METAL=ON.

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash", "scripts/run_all.sh"]
