FROM amazonlinux:2023 AS amazonlinux

ARG PYTHON_VERSION

ENV PYTHONUNBUFFERED=1

RUN yum update -y && \
    yum install -y wget tar make gzip gcc zlib-devel && \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tgz && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py && \
    yum clean all
RUN pip install --upgrade pip

FROM amazonlinux AS python-libs

WORKDIR /app

COPY ta-api/main.py ./main.py
COPY ta-api/ta_api ./ta_api
COPY ta-core/alembic.ini ./alembic.ini
COPY ta-core/alembic ./alembic
COPY ta-core/ta_core ./ta_core
COPY ta-ml/checkpoints/torch_model.ckpt ./checkpoints/torch_model.ckpt
COPY ta-ml/ta_ml ./ta_ml

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt
