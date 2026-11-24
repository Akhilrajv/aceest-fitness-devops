FROM python:3.9-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY database.py .
COPY templates/ templates/

FROM base AS test

COPY tests/ tests/

CMD ["python", "-m", "pytest", "-v"]

FROM base AS production

RUN useradd --uid 1000 --create-home appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
