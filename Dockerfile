FROM python:3.9-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

FROM base AS test

COPY tests/ tests/

CMD ["python", "-m", "pytest", "-v"]

FROM base AS production

EXPOSE 5000

CMD ["python", "app.py"]
