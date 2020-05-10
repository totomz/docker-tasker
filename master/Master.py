import boto3
import json
import os
import sys
import logging
import datetime
import jobs.autotrader.CalculateInversions as Inversions
from jobs.autotrader import BacktestInversions

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])



'''
* Prende in input una funzione che genera i comandi (producer) ed una funzione che parsa i risultati parziali (reducer)
* init() => crea 2 code su SQS, una lotta di istanze spot, ci installa docker e ci fa pull delle immagini
* genera i comandi e li scrive in una coda
* polla la coda con i risultati e scarica il reducer
'''




class Master:

    def __init__(self,
                 supplier=lambda x: x,
                 reducer=lambda x: x,
                 terminate=lambda x: x):
        self.supplier = supplier
        self.reducer = reducer
        self.terminate = terminate

    def start(self):
        logging.info("Starting...")
        aws_region = boto3.session.Session().region_name
        sqs = boto3.client('sqs')
        aws_account_id = boto3.client('sts').get_caller_identity().get('Account')

        queue_jobs = "https://{}.queue.amazonaws.com/{}/{}".format(aws_region, aws_account_id, os.environ['Q_TASK'])
        queue_results = "https://{}.queue.amazonaws.com/{}/{}".format(aws_region, aws_account_id, os.environ['Q_RESULTS'])

        logging.info("Task queue: {}".format(queue_jobs))
        logging.info("Results queue: {}".format(queue_results))

        tasks_submitted = {}

        # Push the task in the queue
        for task in self.supplier():
            body = json.dumps(task)
            response = sqs.send_message(
                QueueUrl=queue_jobs,
                DelaySeconds=1,
                MessageBody=body
            )
            tasks_submitted[task['id']] = response['MessageId']
            logging.info("Queued {} ".format(body))

        # Collect the results.
        accumulator = list()
        keep_polling = True
        empty_counter = 0

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
                    # TODO Print a pecentage
                    self.reducer(result, accumulator)
                    keep_polling = False if len(tasks_submitted) == 0 else True
            except KeyError:
                print("No jobs found....")
                empty_counter += 1
                # keep_polling = False if empty_counter > 10 or len(tasks_submitted) == 0 else True
                continue

        self.terminate(accumulator)


def supply():
    n = 1
    while n <= 10:
        task = {
            "id": "test-{}".format(n),
            "image": "ubuntu",
            "arguments": "/bin/bash -c 'sleep 10; echo {}'".format(n)
        }
        yield task
        n += 1


def reduce(value, accumulator):
    logging.info("    --> Reduce {} [{}]".format(value, accumulator))
    if value['isSuccess']:
        accumulator.append(int(value['payload']))


def termination(values):
    logging.info("Termination! Values: {}".format(values))
    sum = 0
    for v in values:
        sum += v

    logging.info("DONE! The sum is")
    logging.info(sum)


if __name__ == '__main__':
    master = Master(supplier=BacktestInversions.supply,
                    reducer=BacktestInversions.reduce,
                    terminate=BacktestInversions.termination)
    master.start()
    print("### DONE ###")


