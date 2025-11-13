FROM python:3.14-slim AS build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=/usr/local/bin/python3 \
    UV_PROJECT_ENVIRONMENT=/venv

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --locked \
        --no-dev

FROM python:3.14-slim AS production

RUN useradd macau -u 1000

USER macau
WORKDIR /app
EXPOSE 8000

COPY --from=build --chown=macau:macau /venv /venv

COPY --chown=macau ./manage.py ./manage.py
COPY --chown=macau ./macau ./macau

ENV PATH=/venv/bin:$PATH \
    DEBUG=false \
    PYTHONUNBUFFERED=1 \
    GRANIAN_INTERFACE=wsgi \
    GRANIAN_HOST=0.0.0.0 \
    GRANIAN_PORT=8000 \
    GRANIAN_WORKERS_LIFETIME=1800 \
    GRANIAN_RESPAWN_INTERVAL=10 \
    GRANIAN_PROCESS_NAME=macau \
    GRANIAN_RESPAWN_FAILED_WORKERS=1 \
    GRANIAN_BACKPRESSURE=100 \
    GRANIAN_LOG_ACCESS_ENABLED=true

RUN SECRET_KEY=none python manage.py collectstatic --noinput --clear

CMD ["bash", "-c", "./manage.py migrate && granian macau.wsgi:application"]
