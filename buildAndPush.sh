#!/bin/bash

TAG=latest
docker build -t trader/worker:$TAG .
docker tag trader/worker:$TAG 173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/worker:$TAG
docker push 173649726032.dkr.ecr.eu-west-1.amazonaws.com/trader/worker:latest
