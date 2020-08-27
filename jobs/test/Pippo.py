import logging
from datetime import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path

from master.Master import Master

log = logging.getLogger(__name__)


class Pippo:

    def __init__(self):
        print("Ciao")

    """
        Ritorna un prefisso che sara' usato nella generazione dei task
        Questo prefisso viene usato come path nel quale salvare i dati su S3  
    """
    def title(self):
        return "yep_{date}".format(date=datetime.now().strftime('%Y%m%d_%H_%M'))

    def hosts(self):
        # return ["autbob", "192.168.100.238"]
        return []

    def worker_image(self):
        return "ubuntu"

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
        # for file in onlyfiles:
        for file in ["20190701-DIS", "20190701-NFLX"]:
            (day, stock) = Path(file).stem.split("-")
            task = {
                "id": "{prefix}-{suffix}".format(prefix=self.title(),
                                                 suffix=file),
                "arguments": "/bin/bash -c 'sleep 3; echo \"daje\"'"
                # "image": "ubuntu"   # The image is forced by the Master, by calling self.worker_image().
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
    master = Master(job=Pippo())
    master.initialize()
    master.start()
    print("### DONE ###")
