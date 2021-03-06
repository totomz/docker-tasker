import logging
import sys
import os
from tasker.master.Master import Master
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])


def supply():
    n = 1
    while n <= 10:
        task = {
            "id": "test-{}".format(n),
            "image": "ubuntu",
            "arguments": "/bin/bash -c 'sleep 1; echo {number}'".format(number=n)
        }
        yield task
        n += 1


def reduce(value, accumulator, bar):
    # value is a dictionary similar to {'id': 'test-2', 'isSuccess': True, 'payload': '2'}
    bar.text("Processing: {task}".format(task=value['id']))
    if value['isSuccess']:
        accumulator.append(int(value['payload']))


def termination(values):
    logging.info("Termination! Values: {}".format(values))
    _sum = 0
    for v in values:
        _sum += v

    logging.info("DONE! The sum is {}".format(_sum))
    logging.info(_sum)


if __name__ == '__main__':
    print("DIOCANE PYTHON")
    master = Master(supplier=supply,
                    reducer=reduce,
                    terminate=termination)
    master.start()
    print("### DONE ###")
