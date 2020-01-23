FROM python:3

RUN apt-get update && apt-get install -y pipenv
WORKDIR /opt/tasker


COPY Pipfile ./
COPY Pipfile.lock ./

# Run this asap. We change the code and pipenv is slowwwwwww
RUN pipenv install

COPY agent ./agent
COPY master ./master

COPY run.sh /opt/tasker/
ENTRYPOINT ["/opt/tasker/run.sh"]
CMD ["run"]