FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir . && useradd -m app
USER app
ENTRYPOINT ["browserbridge-mcp"]
