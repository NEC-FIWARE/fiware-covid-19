FROM python:3.9-slim

WORKDIR /app

COPY ./aggregator.py /app
COPY ./libs /app/libs
COPY ./requirements.txt .

RUN /usr/local/bin/python -m pip install --upgrade pip \
    && pip install -r requirements.txt

WORKDIR /work

ENTRYPOINT ["python3","/app/aggregator.py"]
