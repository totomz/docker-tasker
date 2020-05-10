import datetime
import json
import logging
import sys
import tempfile

from os import listdir
from os.path import isfile, join
from pathlib import Path

import boto3

from master import Master


def supply():
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
    path = "/Users/totomz/Documents/trading/autotrader/data/quantum"
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    for file in onlyfiles:
    # for file in ["20190701-DIS", "20190701-NFLX"]:
        (day, stock) = Path(file).stem.split("-")
        print(day)
        print(stock)
        task = {
            "id": "trade_on_inv_01-{day}-{stock}".format(day=day, stock=stock),
            "image": "173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/inversion:latest",
            "arguments": "backtest_v1 datadir=s3://autotrader-0291/data/quantum/v1 day={day} stock={stock} inv_store=s3://autotrader-0291/data/quantum_inversions/20200507".format(
                day=day,
                stock=stock
            )
        }
        yield task


def reduce(value, accumulator):
    logging.info("    --> Reduce {} [{}]".format(value, accumulator))
    # DO NOTHING - the worker push the payload to S3

def termination(values):
    logging.info("Termination! ")

    # sum = 0
    # for v in values:
    #     sum += v
    #
    # logging.info("DONE! The sum is")
    # logging.info(sum)
