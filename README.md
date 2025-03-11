## Getting Started

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
