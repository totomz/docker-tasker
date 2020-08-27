import logging
import sys

from os import listdir
from os.path import isfile, join
from pathlib import Path


def supply():
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
    path = "/Users/totomz/Documents/trading/autotrader/data/quantum"
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    for file in onlyfiles:
        (day, stock) = Path(file).stem.split("-")
        print(day)
        print(stock)
        task = {
            "id": "test-{day}-{stock}".format(day=day, stock=stock),
            "image": "173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/inversion:latest",
            "arguments": "inversions datadir=s3://autotrader-0291/data/quantum/v1 day={day} stock={stock} outputdir=s3://autotrader-0291/data/quantum_inversions/20200507".format(
                day=day,
                stock=stock
            )
        }
        yield task


def reduce(value, accumulator):
    logging.info("    --> Reduce {} [{}]".format(value, accumulator))
    # if value['isSuccess']:
    #     accumulator.append(int(value['payload']))


def termination(values):
    logging.info("Termination! Values: {}".format(values))
    # sum = 0
    # for v in values:
    #     sum += v
    #
    # logging.info("DONE! The sum is")
    # logging.info(sum)
