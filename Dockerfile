FROM python:3.12-slim-bookworm AS requirements
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN apt update \ 
    && apt install build-essential -y  \ 
    && uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm AS base
RUN groupadd app && useradd -g app --home-dir /app --create-home app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
RUN apt update && apt install libpq-dev  \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    qpdf \
    libreoffice \
    pandoc -y
RUN chown -R app /app && chmod -R 700 /app

FROM base AS production
COPY --from=requirements /app/.venv /app/.venv
COPY ./dune ./dune
COPY ./credentials.json ./credentials.json
USER app
