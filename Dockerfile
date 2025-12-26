# Sovereign Sanctum Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir cryptography

# Copy Source Code
COPY agent_scribe.py .
COPY governance governance/
COPY intent.yaml .
# Note: We do NOT copy keys/. Keys must be mounted at runtime via Secrets.

# Create artifacts directory for binding
RUN mkdir -p artifacts/triad

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV SANCTUM_PASSPHRASE="sunflower" 
# In production, pass SANCTUM_PASSPHRASE as an env var override!

CMD ["python3", "agent_scribe.py"]
