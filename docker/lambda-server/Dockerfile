FROM public.ecr.aws/lambda/python:3.12

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

RUN ./dev/poetry-all export -f requirements.txt -o requirements.txt --without-hashes
RUN pip install \
    -r ta-api/requirements.txt \
    -r ta-cli/requirements.txt \
    -r ta-core/requirements.txt

WORKDIR /app/ta-api

CMD [ "main.lambda_handler" ]
