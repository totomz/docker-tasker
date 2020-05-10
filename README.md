# docker-tasker

`tasker` is a simple task producer-consumer tool, based on Docker. 

A `master` node is responsible to create jobs, that are pushed to an AWS SQS queue. These jobs are then consumed by as many `agents` you deploy on your nodes. 

## How to run
### What you need
* python3
* docker
* aws access key and secret key

On each worker node
* Run the agent
    -e AWS_ACCESS_KEY_ID=AKIAxxxxx \
    -e AWS_SECRET_ACCESS_KEY=yyyyyyyy \

```bash
AWS_ACCESS_KEY_ID=AKIASQ3SURJILVRL2SV3 AWS_SECRET_ACCESS_KEY=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 aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 173649726032.dkr.ecr.eu-west-1.amazonaws.com

docker pull 173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/worker:latest

docker run --rm -d \
    -e AWS_ACCESS_KEY_ID=AKIASQ3SURJILVRL2SV3 \
    -e AWS_SECRET_ACCESS_KEY=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 \
    -e AWS_DEFAULT_REGION=eu-west-1 \
    -e Q_TASK=task \
    -e Q_RESULTS=results \
    -v /var/run/docker.sock:/var/run/docker.sock \
    173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/worker:latest
```

On the `master`:
1. `git clone git@github.com:totomz/docker-tasker.git`
2. Implement the functions `master.Master.supply`, `master.Master.reduce`, `master.Master.termination`



## Components

### Task
A task is a JSON-encoded message published in an [AWS SQS queue](https://aws.amazon.com/sqs/):
```
{
    "id": "task-1",
    "image": "ubuntu",
    "arguments": "/bin/bash -c 'sleep 10; echo 1'"
}
``` 

A task must have: 
* an `id` as unique identifier;
* the Docker `image` to run;
* the `arguments ` to pass to the `docker run` command;

The above task results in this command
```
docker run ubuntu /bin/bash -c 'sleep 10; echo {"result": 1}'
```  

The result of a computation is encoded in a Result object:
```
{
    "id": "task-1:,
    "isSuccess": true,
    "payload": "anything"

}
```

The result has the same `id` of its task. The last string returned by the docker image is copied in `payload`  

### Master
The [master](https://github.com/totomz/docker-tasker/blob/master/master/Master.py) is a simple Python script that push 
the tasks in the queu and wait for the results. 

The master is configured by passing to it 3 methods:
* `supply()`: a method that return an iterables with the task to run
* `reduce(value, accumulator)`: a function that collects all the outputs
* `termination(values)` : a final function called at the end of the computation

See [the examples](https://github.com/totomz/docker-tasker/blob/master/test/SimpleSum.py).

To run the master:
```
Q_TASK=task Q_RESULTS=results pipenv run python3 -m test.SimpleSum
```


### Agent
The agent is a docker image that runs the tasks. As simple as:
```
docker run --rm -d \
    -e AWS_ACCESS_KEY_ID=AKIAxxxxx \
    -e AWS_SECRET_ACCESS_KEY=yyyyyyyy \
    -e AWS_DEFAULT_REGION=eu-west-1 \
    -e Q_TASK=task \
    -e Q_RESULTS=results \
    -v /var/run/docker.sock:/var/run/docker.sock \
    totomz/docker-tasker:latest 
```

* `Q_TASK` is the name (the name only, not the url) to the input queue
* `Q_RESULTS` is the name (the name only, not the url) to the output queue
