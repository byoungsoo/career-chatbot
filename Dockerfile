FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev

COPY app_bedrock_advanced.py tools.py ./
COPY me/ ./me/

EXPOSE 7860

CMD ["/app/.venv/bin/python", "app_bedrock_advanced.py"]
