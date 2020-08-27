import json
import logging
import os
import sys
from alive_progress import alive_bar

import boto3
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger("master")


class Master:

    def __init__(self, supplier=None, reducer=None, terminate=None):
        self.supplier = supplier
        self.reducer = reducer
        self.terminate = terminate

    def start(self):
        log.info("Starting...")
        aws_region = boto3.session.Session().region_name
        sqs = boto3.client('sqs')
        aws_account_id = boto3.client('sts').get_caller_identity().get('Account')

        queue_jobs = "https://{}.queue.amazonaws.com/{}/{}".format(aws_region, aws_account_id, os.environ['Q_TASK'])
        queue_results = "https://{}.queue.amazonaws.com/{}/{}".format(aws_region, aws_account_id, os.environ['Q_RESULTS'])

        log.info("Task queue: {}".format(queue_jobs))
        log.info("Results queue: {}".format(queue_results))

        tasks_submitted = {}

        # Push the task in the queue
        log.info("Pushing tasks to SQS")
        with alive_bar() as bar:
            for task in self.supplier():
                body = json.dumps(task)
                response = sqs.send_message(
                    QueueUrl=queue_jobs,
                    DelaySeconds=1,
                    MessageBody=body
                )
                tasks_submitted[task['id']] = response['MessageId']
                # log.info("Queued {} ".format(body))
                bar()

        # Collect the results.
        accumulator = list()
        keep_polling = True
        empty_counter = 0

        print(" ")
        log.info("Waiting for the results!")

        with alive_bar(len(tasks_submitted)) as bar:
            while keep_polling:
                resp = sqs.receive_message(
                    QueueUrl=queue_results,
                    AttributeNames=['All'],
                    MaxNumberOfMessages=10,
                    VisibilityTimeout=120,
                    WaitTimeSeconds=20
                )

                message = None
                total_task = len(tasks_submitted)
                try:
                    for message in resp['Messages']:
                        body = message['Body']
                        result = json.loads(body)
                        sqs.delete_message(QueueUrl=queue_results, ReceiptHandle=message['ReceiptHandle'])
                        del tasks_submitted[result['id']]
                        self.reducer(result, accumulator, bar)
                        bar()
                        keep_polling = False if len(tasks_submitted) == 0 else True
                except KeyError:
                    empty_counter += 1
                    keep_polling = False if empty_counter > 10 or len(tasks_submitted) == 0 else True
                    # continue

        self.terminate(accumulator)




