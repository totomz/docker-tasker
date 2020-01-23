import logging
import sys
import os

from master.Master import Master

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])


def supply():

    files = os.listdir("./")

    for f in files:
        if not "AMZN" in f:
            continue
        n = f.split('.')[0]
        t = n.split('-')

        task = {
            "id": n,

            "arguments": "run day={} stock={}".format(t[0], t[1])
        }
        yield task


def reduce(value, accumulator):
    logging.info("    --> Reduce {} [{}]".format(value, accumulator))


def termination(values):
    logging.info("Termination!")


if __name__ == '__main__':

    master = Master(supplier=supply,
                    reducer=reduce,
                    terminate=termination)
    master.start()
    print("### DONE ###")