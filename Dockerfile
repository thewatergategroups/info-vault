FROM python:3.12-slim-bookworm AS base_requirements
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

FROM base_requirements AS requirements
RUN uv sync --frozen --no-dev

FROM requirements AS dev_requirements
RUN uv sync --frozen

FROM python:3.12-slim-bookworm AS base
RUN groupadd app && useradd -g app --home-dir /app --create-home app
WORKDIR /app 
ENV PATH="/app/.venv/bin:$PATH"
COPY  ./scripts/start.sh ./
COPY ./dp ./dp
RUN chown -R app /app && chmod -R 700 /app
USER app
ENTRYPOINT ["bash","start.sh"]

FROM base AS development
COPY --from=dev_requirements /app/.venv /app/.venv

FROM base AS production
COPY --from=requirements /app/.venv /app/.venv
