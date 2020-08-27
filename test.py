import subprocess
import socket
import time
CARBON_SERVER = 'graphite01.eu-west-1.fa823d63acb5bfcaea501aec7bc89fcf.hakunacloud.com'
CARBON_PORT = 2023


def str2float(string, default=0.0):
    res = default
    try:
        res = float(string)
    except Exception:
        res = default

    return res


def collect_and_send(hostname, ip):
    try:
        out = subprocess.check_output("ipmitool -P root -U root -H {ip} sensor".format(ip=ip),
                                      stderr=subprocess.STDOUT,
                                      shell=True)
        stdout = out.decode('utf-8')
        print(":::::")
        print(stdout)
        print(":::::")
        metrics = stdout.split("\n")
        for line in metrics:
            metric_line = line.lower()

            if "fan" not in metric_line and "temp" not in metric_line:
                continue

            p = metric_line.split("|")
            metric_name = str.lower(str.strip(str.strip(p[0]))).replace(" ", "_")
            metric_value = str2float(str.strip(p[1]), 0)
            send_metric(host=hostname, metric_name=metric_name, metric_value=metric_value)

    except Exception as e:
        # do nothing
        print(e)


def send_metric(host, metric_name, metric_value):
    message = 'totomz.cluster.{host}.bmc.{metric} {value} {time:d}\n'.format(host=host,
                                                                             metric=metric_name,
                                                                             value=metric_value,
                                                                             time=int(time.time()))
    print(message)
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(message.encode())
    sock.close()


while True:
    print("*")
    collect_and_send(hostname="ziocharlie", ip="192.168.100.37")
    collect_and_send(hostname="ziobob", ip="192.168.100.31")
    time.sleep(10)

