FROM docker-registry.ebrains.eu/hdc-services-image/base-image:python-3.10.12-v2 AS production-environment

ENV PYTHONDONTWRITEBYTECODE=true \
    PYTHONIOENCODING=UTF-8 \
    POETRY_VERSION=1.3.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="${POETRY_HOME}/bin:${PATH}"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential

# Having curl installed in the image is a potential security liability
# So we remove it once we don't need it anymore
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get remove curl -y

COPY poetry.lock pyproject.toml ./
COPY notification ./notification

RUN poetry install --no-dev --no-interaction


FROM production-environment AS notification-image

RUN chown -R app:app /app
USER app

ENTRYPOINT ["python3", "-m", "notification"]


FROM production-environment AS development-environment

RUN poetry install --no-interaction


FROM development-environment AS alembic-image

ENV ALEMBIC_CONFIG=migrations/alembic.ini

COPY migrations ./migrations

RUN chown -R app:app /app

USER app

ENTRYPOINT ["python3", "-m", "alembic"]

CMD ["upgrade", "head"]
