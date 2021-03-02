FROM python:3.9-slim

RUN /usr/local/bin/python -m pip install --upgrade pip \
    && pip install meteoroid-cli
WORKDIR /work

ENTRYPOINT ["/usr/local/bin/meteoroid"]
