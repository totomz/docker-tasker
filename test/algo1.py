import logging
import sys

from master.Master import Master

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])


def supply():
    task = {
        "id": "test-1",
        "image": "jj",
        "arguments": "run day=20190709 stock=AMZN"
    }
    yield task


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
    master = Master(supplier=supply,
                    reducer=reduce,
                    terminate=termination)
    master.start()
    print("### DONE ###")