#!/usr/bin/python3 -u

import os
import boto3
import json
import subprocess
import multiprocessing
import docker
import os

from multiprocessing import Pool

# Create SQS client
# credentials from ~/.boto
sqs = boto3.client('sqs', region_name='us-east-2' )

region = sqs._client_config.region_name

queue_jobs = 'https://%s.queue.amazonaws.com/242728094507/jcalibrador-jobs' % region
queue_results = 'https://%s.queue.amazonaws.com/242728094507/jcalibrador-results' % region


class DockerCommand():
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
    nProc = multiprocessing.cpu_count()
    print("Start polling")
    pool = Pool(processes=nProc)
    for k in range(0, nProc+1):
        print("Starting poller %s" % k)
        pool.apply_async(process_job, ())

    print("MAIN - wait for the pollers to ends")
    pool.close()
    pool.join()


def process_job():
    while True:
        resp = sqs.receive_message(
            QueueUrl=queue_jobs,
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            VisibilityTimeout=120,
            WaitTimeSeconds=2
        )

        message = None
        try:
            message = resp['Messages'][0]
        except KeyError:
            # print("No jobs found....")
            continue

        command = DockerCommand()
        command.set_from_sqs(message['Body'])

        client = docker.from_env(version='auto')
        result = DockerResult(id=command.id)

        try:
            out = client.containers.run(command.image, command.arguments)
            result.isSuccess = True
            result.payload = ''.join(out.splitlines())
        except Exception as e:
            print("ERROR:[%s] JOB:[%s]" % (e.message, message['Body']))
            result.isSuccess = False
            result.payload = e.message

        # Publish the result and remove the job from the queue
        response = sqs.send_message(
            QueueUrl=queue_results,
            MessageBody=result.to_json()
        )

        resp2 = sqs.delete_message(
            QueueUrl=queue_jobs,
            ReceiptHandle=message['ReceiptHandle']
        )
        print("Return %s" % result.payload)


run()