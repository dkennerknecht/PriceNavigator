FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/pyproject.toml
COPY alembic.ini /app/alembic.ini
COPY app /app/app
COPY migrations /app/migrations
COPY scripts /app/scripts

RUN pip install --no-cache-dir .
RUN chmod +x /app/scripts/start.sh /app/scripts/load_seed.sh

EXPOSE 8000

CMD ["/app/scripts/start.sh"]

