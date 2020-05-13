import logging
from datetime import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path

from master.Master import Master

log = logging.getLogger(__name__)


class BacktestInversions:

    def __init__(self):
        self._title = "backtest_inversions_{date}".format(date=datetime.now().strftime('%Y%m%d_%H_%M'))

    def title(self):
        return self._title

    def hosts(self):
        return ["autbob", "autcharlie"]
        # return []

    def worker_image(self):
        return "173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/inversion:latest"

    def host_user(self, host):
        return "totomz"

    def host_pass(self, host):
        return "7ydacw3a"

    def aws_key(self):
        return "AKIASQ3SURJILVRL2SV3"

    def aws_secret(self):
        return "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"

    def supply(self):
        path = "/Users/totomz/Documents/trading/autotrader/data/quantum"
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        for file in onlyfiles:
        # for file in ["20190701-DIS", "20190701-NFLX"]:
            (day, stock) = Path(file).stem.split("-")
            task = {
                "id": "{prefix}-{suffix}".format(prefix=self.title(), suffix=file),
                "arguments": "backtest_v1 day={day} stock={stock} datadir=s3://autotrader-0291/data/quantum/v1 inv_store=s3://autotrader-0291/data/quantum_inversions/20200507".format(
                    day=day,
                    stock=stock
                )
            }
            yield task

    def reduce(self, value, accumulator):
        # the worker push the payload to S3
        if value['isSuccess']:
            log.info("   ---> SUCCESS! {}".format(value['payload']))
        else:
            log.error("   ---> ERROR from worker! {}".format(value['payload']))

    def termination(self, values):
        log.info("Termination! ")


if __name__ == '__main__':
    master = Master(job=BacktestInversions())
    master.initialize()
    master.start()
    print("### DONE ###")
