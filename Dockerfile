FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql \
    postgresql-contrib \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN chmod +x /app/scripts/entrypoint.sh

ENV PYTHONPATH=/app
ENV PORT=8080
ENV APP_MODULE=services.approval_ui.app:app

EXPOSE 8080

CMD ["/app/scripts/entrypoint.sh"]
