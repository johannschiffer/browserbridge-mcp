FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir . && useradd -m -u 10001 appuser && mkdir -p /data && chown -R appuser:appuser /app /data
ENV BROWSERBRIDGE_DB_PATH=/data/receipts.db
USER appuser
ENTRYPOINT ["browserbridge-mcp"]
