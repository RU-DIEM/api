# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.12.1-trixie-slim AS base

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_MANAGED_PYTHON=true \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_INSTALL_DIR=/opt/python

WORKDIR /app

COPY .python-version ./

RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv uv python install

COPY pyproject.toml uv.lock ./

########################################################################################

FROM base AS deps-dev

RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv uv sync --frozen --all-groups

########################################################################################

FROM base AS deps-prod

RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv uv sync --frozen --no-dev

########################################################################################

FROM debian:trixie-slim AS runtime-base

ENV DJANGO_SETTINGS_MODULE=api_core.settings \
    GRANIAN_HOST=0.0.0.0 \
    GRANIAN_INTERFACE=asginl \
    GRANIAN_PORT=8080 \
    GRANIAN_WORKING_DIR=/app/src \
    PATH=/opt/venv/bin:$PATH \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install --no-install-recommends --yes ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --system rudi && \
    useradd --create-home --gid rudi --home-dir /app --system rudi

WORKDIR /app

COPY --from=base /opt/python /opt/python

COPY --chown=rudi:rudi pyproject.toml ./
COPY --chown=rudi:rudi src/ ./src/

EXPOSE 8080

########################################################################################

FROM runtime-base AS runtime-dev

ENV GRANIAN_RELOAD_PATHS=$GRANIAN_WORKING_DIR

COPY --from=deps-dev /opt/venv /opt/venv

USER rudi

CMD ["granian", "api_core.asgi:application", "--access-log", "--reload"]

########################################################################################

FROM runtime-base AS runtime-prod

COPY --from=deps-prod /opt/venv /opt/venv

USER rudi

CMD ["granian", "api_core.asgi:application", "--access-log"]
