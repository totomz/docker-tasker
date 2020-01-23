# docker-tasker

TODO README 


# Agent
The agent is a docker image that runs task i

```
docker run --name worker \
    -e AWS_ACCESS_KEY_ID=AKIAxxxx \
    -e AWS_SECRET_ACCESS_KEY=yyyyyyy \
    -e AWS_DEFAULT_REGION=eu-west-1 \
    -e Q_TASK=task \
    -e Q_RESULTS=results \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -d \
    hakunacloud/tasker:latest 

```

