FROM python:3.11.4-slim-bookworm as base-image

ARG DEV="false"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /backend

ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME="/usr/local/bin/poetry" \
    POETRY_VERSION=1.6.1 \
    PATH="$PATH:$POETRY_HOME/bin"

# Copy settings
COPY ./backend/poetry.lock ./backend/pyproject.toml ./backend/settings.yaml /backend/

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Install app dependencies
RUN poetry config virtualenvs.create false && \
    if [ $DEV = "true" ]; \
    then poetry install; \
    else poetry install --no-dev; \
    fi

# Copy app
COPY ./backend/src /backend/src

FROM base-image as test-image

COPY ./backend/tests /backend/tests

FROM base-image as release-image

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

# Prepare entrypoint.sh
COPY ./backend/docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh  \
    && chmod +x /entrypoint.sh

WORKDIR /backend/src

USER app

ENTRYPOINT ["/entrypoint.sh"]
