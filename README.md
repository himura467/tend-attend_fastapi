## Local Setup

We will be using `pyenv`, `poetry` and `docker`.

### Python installation using pyenv

https://github.com/pyenv/pyenv

```sh
pyenv install `cat .python-version`
```

### Dependencies installation using Poetry

https://python-poetry.org

```sh
poetry config virtualenvs.in-project true
./dev/poetry-all.sh install
```

### Build and run the application using Docker Compose

https://docs.docker.com/compose

```sh
docker compose up
```

### Run an ASGI web server using uvicorn

Please make sure that the appropriate `.env` files are in place before running.

```sh
cd ta-api
poetry run uvicorn main:app --reload
```
