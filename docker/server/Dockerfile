FROM python:3.12.7

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

WORKDIR /app

COPY ta-api ./ta-api
COPY ta-cli ./ta-cli
COPY ta-core ./ta-core

COPY dev ./dev

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN ./dev/poetry-all.sh install

WORKDIR /app/ta-api

CMD [ "poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
