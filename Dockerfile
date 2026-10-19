FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/models/huggingface \
    HF_HUB_OFFLINE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir \
    torch==2.11.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu
COPY pyproject.toml README.md requirements.txt ./
COPY constraints/ ./constraints/
COPY src/ ./src/
COPY configs/ ./configs/
RUN python -m pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "rag_agent_system.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]