FROM public.ecr.aws/lambda/python:3.12

ENV PYTHONUNBUFFERED=1

COPY ta-api/main.py ./main.py
COPY ta-api/ta_api ./ta_api
COPY ta-cli/main.py ./cli_main.py
COPY ta-cli/ta_cli ./ta_cli
COPY ta-core/ta_core ./ta_core

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt

CMD [ "main.lambda_handler" ]
