# docker-tasker

docker-tasker, or `dt`, allows you to easily run tasks on a cluster of instances and collect the results.

As an example, you could evaluate an expensive cost function of a genetic algorithm on a cluster of cpu with few lines of code. 
  
With `dt` you can
* create a cluster of instances;
* zip your strategy in a Docker container;
* run your container on all the nodes of the cluster;
* collect and evaluate the results;


`dt` has  the following components


  