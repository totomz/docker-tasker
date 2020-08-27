import logging
import sys

from os import listdir
from os.path import isfile, join
from pathlib import Path


def supply():
    n = 1
    while n <= 1:
        task = {
            "id": "test-{}".format(n),
            "image": "ubuntu",
            "arguments": "/bin/bash -c \"sleep 2; echo '{\"pippo\":\'pluto\", \"age\": 23}'\"".format(n)
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
