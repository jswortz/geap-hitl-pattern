FROM python:3.12-slim-bookworm
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
ENV PYTHONPATH=/app
ENV PORT=8001
CMD ["uvicorn", "services.trend_agent.main:app", "--host", "0.0.0.0", "--port", "8001"]
