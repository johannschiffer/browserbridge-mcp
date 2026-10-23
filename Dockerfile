# Generated for Glama.ai and Smithery.ai MCP registry compliance
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .
ENTRYPOINT ["browserbridge-mcp"]
