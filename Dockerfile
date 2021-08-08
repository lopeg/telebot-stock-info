FROM python:3.8.5-slim-buster as python-base
# Create shared ENV VARs for setup and runtime
ENV POETRY_VERSION="1.1.4" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    SETUP_PATH="/opt/app"

# Add our to-be-created virtualenv to PATH
ENV PATH="$SETUP_PATH/.venv/bin:$PATH"
WORKDIR $SETUP_PATH

# Install all dependencies in cache-friendly way with Poetry, see:
#   https://github.com/python-poetry/poetry/issues/1301
COPY pyproject.toml poetry.lock ./
RUN python3 -m pip install "poetry==$POETRY_VERSION" && \
    poetry install --no-root --no-dev

COPY suid_bot suid_bot

FROM python:3.8.5-slim-buster as production

ENV SETUP_PATH="/opt/app"
WORKDIR $SETUP_PATH
COPY --from=python-base $SETUP_PATH $SETUP_PATH

# Add our virtualenv to PATH
ENV PATH="$SETUP_PATH/.venv/bin:$PATH"
ENTRYPOINT ["python", "suid_bot/bot.py"]

