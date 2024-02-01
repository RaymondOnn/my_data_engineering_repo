FROM python:3.10

WORKDIR /usr/src/app
RUN --mount=type=bind,source=./web2kafka/requirements.txt,target=/tmp/requirements.txt  \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./web2kafka/src/ .

CMD ["python", "./hello.py"]
