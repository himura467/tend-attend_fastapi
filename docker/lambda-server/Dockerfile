FROM public.ecr.aws/lambda/python:3.10

ENV PYTHONUNBUFFERED=1
RUN yum update -y && yum install -y git
RUN pip install --upgrade pip

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

CMD [ "main.lambda_handler" ]
