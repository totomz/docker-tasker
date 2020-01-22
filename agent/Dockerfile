FROM python:3

WORKDIR /usr/src/app

COPY worker.py ./
RUN pip install --no-cache-dir boto3 json-extension docker

COPY agent .

CMD [ "python", "./worker.py" ]