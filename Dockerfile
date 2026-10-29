FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY service/ ./service/
RUN useradd --uid 1001 --create-home appuser && \
    chgrp -R 0 /app && chmod -R g=u /app

USER 1001
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--log-level", "info", "--access-logfile", "-", "service:app"]
