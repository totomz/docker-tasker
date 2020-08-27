# tasker-agent
Agent is a docker container that run more docker containers. 
It polls task definitions from a queue, launch a container and get the result

A task definition is a JSON object defined as below
```
{
  "id: "unique identifier for this task",
  "image": "docker image to run, eg `ubuntu`",
  "command": "the command to execute, eg `/bin/bash -c 'echo 1'` ": 
}
```