#!/usr/bin/python3 -u

import json
import logging
import multiprocessing
import os
import sys
import tempfile
import boto3
import docker
from datetime import datetime
from multiprocessing import Pool

from dotenv import load_dotenv
load_dotenv()

nProc = int(os.getenv('nProc', multiprocessing.cpu_count()))

sqs = boto3.client('sqs')

aws_region = boto3.session.Session().region_name
aws_account_id = boto3.client('sts').get_caller_identity().get('Account')
queue_jobs_name = os.environ['Q_TASK']
queue_results_name = os.environ['Q_RESULTS']

queue_jobs = "https://{}.queue.amazonaws.com/{}/{}".format(aws_region, aws_account_id, queue_jobs_name)
queue_results = "https://{}.queue.amazonaws.com/{}/{}".format(aws_region, aws_account_id, queue_results_name)


class DockerCommand:
    def __init__(self, id="", command="run", image='ubuntu', arguments='sleep 1; echo 3'):
        self.command = command
        self.image = image
        self.id = id
        self.arguments = arguments

    def set_from_sqs(self, message):
        job = json.loads(message)
        self.image = job['image']
        self.id = job['id']
        self.arguments = job['arguments']


class DockerResult:
    def __init__(self, id="", isSuccess="", payload=""):
        self.id = id
        self.isSuccess = isSuccess
        self.payload = payload

    def to_json(self):
        return json.dumps({
            'id': self.id,
            'isSuccess': self.isSuccess,
            'payload': self.payload
        })


def run():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(threadName)s: %(message)s'))
    log.addHandler(handler)

    logging.info("Start polling")
    pool = Pool(processes=nProc)
    for k in range(0, nProc+1):
        logging.info("Starting poller %s" % k)
        pool.apply_async(process_job, ())

    logging.info("MAIN - wait for pollers to end")
    pool.close()
    pool.join()


def process_job():
    log = multiprocessing.get_logger()
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('    --> [%(asctime)s] - %(processName)s - %(message)s'))
    log.addHandler(handler)

    log.info("Poller started polling")
    while True:
        resp = sqs.receive_message(
            QueueUrl=queue_jobs,
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            VisibilityTimeout=120,
            WaitTimeSeconds=20
        )

        message = None
        try:
            message = resp['Messages'][0]
        except KeyError:
            # print("No jobs found....")
            continue

        command = DockerCommand()
        command.set_from_sqs(message['Body'])

        log.info("GOT a task: {}".format(command.id))

        try:
            client = docker.from_env()
            result = DockerResult(id=command.id)

            start = datetime.utcnow()

            tmp = command.image.split(":")
            image_tag = "latest" if len(tmp) == 1 else tmp[1]
            out = client.containers.run(command.image, command.arguments).decode("utf-8").rstrip()

            # Assumption: the result is exactly the last output I got from the container
            out = out.split("\n")[-1]

            log.info("Partial result: [{}] in {}".format(out, datetime.utcnow() - start))
            result.isSuccess = True
            result.payload = ''.join(out.splitlines())
        except Exception as e:
            error_message = "general error"

            if isinstance(e, ValueError):
                error_message = str(e)
            elif hasattr(e, 'stderr'):
                # The child container went in error
                error_message = e.stderr.decode("utf-8")
            elif hasattr(e, 'explanation'):
                # Docker api error
                error_message = e.explanation

            log.error("ERROR:[%s] JOB:[%s]" % (error_message, message['Body']))
            result.isSuccess = False
            result.payload = error_message

        # Publish the result and remove the job from the queue
        sqs.send_message(
            QueueUrl=queue_results,
            MessageBody=result.to_json()
        )

        sqs.delete_message(
            QueueUrl=queue_jobs,
            ReceiptHandle=message['ReceiptHandle']
        )


run()