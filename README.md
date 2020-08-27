# docker-tasker

`docker-tasker` is a remote producer-consumer framework based on Docker. 

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

A task **must** have: 
* an `id` that uniquely identifies each task;
* the Docker `image` to run;
* the `arguments ` to pass to the `docker run` command;
 

The result of a computation is encoded in a Result object:
```
{
    "id": "task-1:,
    "isSuccess": true,
    "payload": "the last line found in container STDOUT/STDERR"

}
```
The result has the same `id` of its task. The last string returned by the docker image is returned as `payload`  

### Master
The [master](https://github.com/totomz/docker-tasker/blob/master/master/Master.py) is a simple Python script that push 
the tasks in the [AWS SQS queue](https://aws.amazon.com/sqs/) and wait for the results. 

The master is configured by passing to it 3 methods:
* `supply()`: a method that return an iterables with the task to run
* `reduce(value, accumulator)`: a function that collects all the outputs
* `termination(values)`: a final function called at the end of the computation

See [the examples](https://github.com/totomz/docker-tasker/blob/master/test/SimpleSum.py).

To run the master:
```
Q_TASK=task Q_RESULTS=results python3 -m test.SimpleSum
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


# Development
Dependencies ar managed with pip. Conda for the envs.
With Conda:
``` 
conda create -n tasker python=3.7 
conda activate tasker
conda install python=3.7
conda install pip
pip install -r requirements.txt
```
