FROM python:3

WORKDIR /opt/tasker

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY tasker/agent ./agent

COPY run.sh /opt/tasker/
ENTRYPOINT ["/opt/tasker/run.sh"]
CMD ["run"]
