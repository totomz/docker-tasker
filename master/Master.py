import json
import logging
import os
import sys

import boto3
import paramiko
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logging.getLogger('paramiko.transport').setLevel(logging.WARNING)
log = logging.getLogger("master")


'''
* Prende in input una funzione che genera i comandi (producer) ed una funzione che parsa i risultati parziali (reducer)
* init() => crea 2 code su SQS, una lotta di istanze spot, ci installa docker e ci fa pull delle immagini
* genera i comandi e li scrive in una coda
* polla la coda con i risultati e scarica il reducer
'''


class Master:

    def __init__(self, job):
        self.supplier = job.supply
        self.reducer = job.reduce
        self.terminate = job.termination
        self.job = job

    def initialize(self):
        log.info("Initializing agents")
        for host in self.job.hosts():
            log.info("Host: {host}".format(host=host))
            log.info("    Stopping running worker")
            self.ssh_command(host, "docker stop dtrader_worker", True)

            log.info("    AWS ECR Login")
            self.ssh_command(host, "aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 173649726032.dkr.ecr.eu-west-1.amazonaws.com")

            log.info("    Pulling image")
            self.ssh_command(host, "docker pull 173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/worker:latest")

    def ssh_command(self, host, command, ignore_errors=False):
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host,
                        username=self.job.host_user(host=host),
                        password=self.job.host_pass(host=host))

            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)

            result = ssh_stdout.channel.recv_exit_status()
            stdout = ssh_stdout.read().decode()
            stderr = ssh_stderr.read().decode()
            if not ignore_errors:
                if result > 0:
                    print("*** ERROR INIT HOST {} ***".format(host))
                    print(stdout)
                    print(stderr)
                    print("***************************")
                    raise Exception("Command returned code {}".format(result))

            return result

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

        for host in self.job.hosts():
            command = """
                docker run --rm -d \
                    --name dtrader_worker \
                    -e AWS_ACCESS_KEY_ID={aws_key} \
                    -e AWS_SECRET_ACCESS_KEY={aws_secret} \
                    -e AWS_DEFAULT_REGION=eu-west-1 \
                    -e Q_TASK=task \
                    -e Q_RESULTS=results \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/worker:latest
                """.format(aws_key=self.job.aws_key(),
                           aws_secret=self.job.aws_secret(),
                           hostname=host)

            log.info("{host} --> Starting agents".format(host=host))
            self.ssh_command(host, command)

            log.info("{host} --> Pulling image".format(host=host))
            self.ssh_command(host, "docker pull {image}".format(image=self.job.worker_image()))

        # Push the task in the queue
        for task in self.supplier():
            task['image'] = self.job.worker_image()
            body = json.dumps(task)
            response = sqs.send_message(
                QueueUrl=queue_jobs,
                DelaySeconds=1,
                MessageBody=body
            )
            tasks_submitted[task['id']] = response['MessageId']
            log.info("Queued {} ".format(body))

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
                print(".")
                empty_counter += 1
                # keep_polling = False if empty_counter > 10 or len(tasks_submitted) == 0 else True
                continue

        self.terminate(accumulator)




