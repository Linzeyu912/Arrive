FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ARRIVE_DATA_DIR=/data

WORKDIR /app

# Native runtime libraries used by the local OCR image backend.
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.lock ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock

COPY pyproject.toml README.md ./
COPY src ./src
COPY migrations ./migrations

RUN python -m pip install --no-cache-dir --no-deps --no-build-isolation .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "arrive.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
