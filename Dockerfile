# Deployed to Render (free tier). Runs as a non-root user and binds to $PORT.

FROM python:3.12-slim

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1
WORKDIR $HOME/app

# Dependencies first: this layer is cached and only rebuilds when they change.
COPY --chown=user:user requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install the ddss package itself (--no-deps: requirements.txt already covers them).
COPY --chown=user pyproject.toml ./
COPY --chown=user src/ ./src/
RUN pip install --no-cache-dir --no-deps .

# Application code last: it changes most often, so it invalidates the least.
COPY --chown=user api/ ./api/

EXPOSE 10000
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
