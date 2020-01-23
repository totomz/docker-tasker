import logging
import sys
from master.Master import Master

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])


def supply():
    n = 1
    while n <= 10:
        task = {
            "id": "test-{}".format(n),
            "image": "ubuntu",
            "arguments": "/bin/bash -c 'sleep 1; echo {}'".format(n)
        }
        yield task
        n += 1


def reduce(value, accumulator):
    logging.info("    --> Reduce {} [{}]".format(value, accumulator))
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
    master = Master(supplier=supply,
                    reducer=reduce,
                    terminate=termination)
    master.start()
    print("### DONE ###")