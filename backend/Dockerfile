FROM ghcr.io/astral-sh/uv:0.13.6 AS uv
FROM python:3.12.16-slim-bookworm AS runtime
COPY --from=uv /uv /uvx /bin/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY backend/ ./
RUN uv sync --frozen --no-dev && groupadd --gid 10001 portfolio && useradd --uid 10001 --gid portfolio --no-create-home portfolio && mkdir -p /data/media && chown -R portfolio:portfolio /data /app
USER portfolio
ENV PATH="/app/backend/.venv/bin:$PATH" MEDIA_ROOT=/data/media
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--no-proxy-headers"]
