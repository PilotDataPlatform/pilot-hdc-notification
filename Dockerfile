FROM python:3.10.7-buster AS production-environment

ENV PYTHONDONTWRITEBYTECODE=true \
    PYTHONIOENCODING=UTF-8 \
    POETRY_VERSION=1.3.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="${POETRY_HOME}/bin:${PATH}"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY poetry.lock pyproject.toml ./
COPY notification ./notification

RUN poetry install --no-dev --no-interaction


FROM production-environment AS notification-image

ENTRYPOINT ["python3", "-m", "notification"]


FROM production-environment AS development-environment

RUN poetry install --no-interaction


FROM development-environment AS alembic-image

ENV ALEMBIC_CONFIG=migrations/alembic.ini

COPY migrations ./migrations

ENTRYPOINT ["python3", "-m", "alembic"]

CMD ["upgrade", "head"]
