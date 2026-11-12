FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY tests/ tests/
COPY pytest.ini .
COPY app.py .

ARG LLM_PROVIDER=ollama
ARG OLLAMA_HOST=http://localhost:11434
ARG MODEL_NAME=qwen3.5:9b-q4_K_M
ARG GEMINI_API_KEY
ARG GEMINI_MODEL=gemini-2.0-flash

ENV LLM_PROVIDER=${LLM_PROVIDER}
ENV OLLAMA_HOST=${OLLAMA_HOST}
ENV MODEL_NAME=${MODEL_NAME}
ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV GEMINI_MODEL=${GEMINI_MODEL}

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
